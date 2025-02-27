# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Property-based testing for TFP platform compatibility.

- GradientTape
- XLA compilation
- tf.vectorized_map

Compatibility with JAX transformations is in jax_transformation_test.py.

General distribution properties are in distribution_properties_test.py.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

from absl.testing import parameterized
import hypothesis as hp
from hypothesis import strategies as hps
import numpy as np
import six
import tensorflow.compat.v2 as tf

from tensorflow_probability.python import distributions as tfd
from tensorflow_probability.python import experimental
from tensorflow_probability.python.distributions import hypothesis_testlib as dhps
from tensorflow_probability.python.internal import hypothesis_testlib as tfp_hps
from tensorflow_probability.python.internal import tensor_util
from tensorflow_probability.python.internal import test_util

XLA_UNFRIENDLY_DISTS = frozenset([
    # TODO(b/159995894): SegmentMean not registered for XLA.
    'Bates',
    # TODO(b/159996837):
    'Categorical',
    # TODO(b/159996484): Continuous Bernoulli nan/inf locations mismatch.
    'ContinuousBernoulli',
    # TODO(b/159997119): Finite discrete produces NaNs.
    'FiniteDiscrete',
    # TODO(b/159996966)
    'Gamma',
    'OneHotCategorical',
    'LogNormal',
    # TODO(b/162935914): Needs to use XLA friendly Poisson sampler.
    'NegativeBinomial',
    # TODO(b/137956955): Add support for hypothesis testing
    'PoissonLogNormalQuadratureCompound',
    # TODO(b/159999573): XLA / non-XLA computation seems to have
    # completely arbitrary differences!
    'Poisson',
    # TODO(b/137956955): Add support for hypothesis testing
    'SinhArcsinh',
    # TruncatedCauchy has log_probs that are very far off.
    'TruncatedCauchy',
    # TODO(b/159997353): StatelessTruncatedNormal missing in XLA.
    'TruncatedNormal',
    'Weibull',
    'WishartTriL',  # log_probs are very far off.
    # TODO(b/159997700) No XLA Zeta
    'Zipf',
])

NO_SAMPLE_PARAM_GRADS = {
    'Deterministic': ('atol', 'rtol'),
}

NO_LOG_PROB_PARAM_GRADS = ('Deterministic', 'Empirical')

NO_KL_PARAM_GRADS = ('Deterministic',)

EXTRA_TENSOR_CONVERSION_DISTS = {
    'RelaxedBernoulli': 1,
    'WishartTriL': 3,  # not concretizing linear operator scale
    'Chi': 2,  # subclasses `Chi2`, runs redundant checks on `df` parameter
}

# TODO(b/130815467) All distributions should be auto-vectorizeable.
# The lists below contain distributions from INSTANTIABLE_BASE_DISTS that are
# blocked for the autovectorization tests. Since not all distributions are
# in INSTANTIABLE_BASE_DISTS, these should not be taken as exhaustive.
SAMPLE_AUTOVECTORIZATION_IS_BROKEN = [
    'Bates',  # tf.repeat and tf.range do not vectorize. (b/157665707)
    'DirichletMultinomial',  # Times out. (b/164143676)
    'Multinomial',  # TensorListConcatV2 fallback broken: b/166658748
    'PlackettLuce',  # No converter for TopKV2
    'Skellam',
    # 'TruncatedNormal',  # No converter for ParameterizedTruncatedNormal
]

LOGPROB_AUTOVECTORIZATION_IS_BROKEN = [
    'Bates',  # tf.repeat and tf.range do not vectorize. (b/157665707)
    'HalfStudentT',  # Numerical problem: b/149785284
    'Skellam',
    'StudentT',  # Numerical problem: b/149785284
    'TruncatedNormal',  # Numerical problem: b/150811273
    'VonMisesFisher',  # No converter for CheckNumerics
    'Wishart',  # Actually works, but disabled because log_prob of sample is
                # ill-conditioned for reasons unrelated to pfor.
    'WishartTriL',  # Same as Wishart.
]

# Vectorization can rewrite computations in ways that (apparently) lead to
# minor floating-point inconsistency.
# TODO(b/142827327): Bring tolerance down to 0 for all distributions.
VECTORIZED_LOGPROB_ATOL = collections.defaultdict(lambda: 1e-6)
VECTORIZED_LOGPROB_ATOL.update({
    'BetaBinomial': 1e-5,
    'CholeskyLKJ': 1e-4,
    'LKJ': 1e-3,
    'PowerSpherical': 1e-5,
})

VECTORIZED_LOGPROB_RTOL = collections.defaultdict(lambda: 1e-6)
VECTORIZED_LOGPROB_RTOL.update({
    'Beta': 1e-5,
    'NegativeBinomial': 1e-5,
    'PERT': 1e-5,
    'PowerSpherical': 5e-5,
})

# TODO(b/142827327): Bring tolerance down to 0 for all distributions.
XLA_LOGPROB_ATOL = collections.defaultdict(lambda: 1e-6)
XLA_LOGPROB_ATOL.update({
    'Beta': 1e-4,
    'BetaBinomial': 5e-6,
    'Binomial': 5e-6,
    'DirichletMultinomial': 1e-4,
    'ExpGamma': 2e-3,  # TODO(b/166257329)
    'ExpInverseGamma': 1.5e-3,  # TODO(b/166257329)
    'ExpRelaxedOneHotCategorical': 3e-5,
    'InverseGamma': 5e-5,
    'Kumaraswamy': 3e-6,
    'Logistic': 3e-6,
    'Multinomial': 2e-4,
    'PowerSpherical': 2e-5,
})

XLA_LOGPROB_RTOL = collections.defaultdict(lambda: 1e-6)
XLA_LOGPROB_RTOL.update({
    'Beta': 5e-4,
    'BetaBinomial': 5e-4,
    'Binomial': 4e-6,
    'Categorical': 6e-6,
    'Chi': 2e-4,
    'Chi2': 5e-5,
    'CholeskyLKJ': 1e-4,
    'ContinuousBernoulli': 2e-6,
    'Dirichlet': 1e-3,
    'DirichletMultinomial': 2e-4,
    'ExpRelaxedOneHotCategorical': 1e-3,  # TODO(b/163118820)
    'ExpGamma': 5e-2,  # TODO(b/166257329)
    'ExpInverseGamma': 5e-2,  # TODO(b/166257329)
    'FiniteDiscrete': 6e-6,
    'GammaGamma': 5e-4,
    'Geometric': 5e-5,
    'InverseGamma': 5e-3,
    'JohnsonSU': 1e-2,
    'LKJ': .07,
    'LogLogistic': 1.5e-2,  # TODO(b/163118820)
    'Multinomial': 3e-4,
    'OneHotCategorical': 1e-3,  # TODO(b/163118820)
    'Pareto': 2e-2,  # TODO(b/159997708)
    'PERT': 5e-4,
    'Poisson': 3e-2,  # TODO(b/159999573)
    'PowerSpherical': .003,
    'RelaxedBernoulli': 3e-3,
    'VonMises': 2e-2,  # TODO(b/160000258):
    'VonMisesFisher': 5e-3,
    'WishartTriL': 1e-5,
})


SKIP_KL_CHECK_DIST_VAR_GRADS = [
    'Kumaraswamy',  # TD's KL gradients do not rely on bijector variables.
    'JohnsonSU'  # TD's KL gradients do not rely on bijector variables.
]


def extra_tensor_conversions_allowed(dist):
  """Returns number of extra tensor conversions allowed for the input dist."""
  extra_conversions = EXTRA_TENSOR_CONVERSION_DISTS.get(type(dist).__name__)
  if extra_conversions:
    return extra_conversions
  if isinstance(dist, tfd.TransformedDistribution):
    return 1
  if isinstance(dist, tfd.BatchReshape):
    # One for the batch_shape_tensor needed by _call_reshape_input_output.
    # One to cover inability to turn off validate_args for the base
    # distribution (b/143297494).
    return 2
  return 0


@test_util.test_all_tf_execution_regimes
class DistributionGradientTapeAndConcretizationTest(test_util.TestCase):

  @parameterized.named_parameters(
      {'testcase_name': dname, 'dist_name': dname}
      for dname in dhps.TF2_FRIENDLY_DISTS)
  @hp.given(hps.data())
  @tfp_hps.tfp_hp_settings()
  def testDistribution(self, dist_name, data):
    seed = test_util.test_seed()
    # Explicitly draw event_dim here to avoid relying on _params_event_ndims
    # later, so this test can support distributions that do not implement the
    # slicing protocol.
    event_dim = data.draw(hps.integers(min_value=2, max_value=6))
    dist = data.draw(dhps.distributions(
        dist_name=dist_name, event_dim=event_dim, enable_vars=True))
    batch_shape = dist.batch_shape
    batch_shape2 = data.draw(tfp_hps.broadcast_compatible_shape(batch_shape))
    dist2 = data.draw(
        dhps.distributions(
            dist_name=dist_name,
            batch_shape=batch_shape2,
            event_dim=event_dim,
            enable_vars=True))
    self.evaluate([var.initializer for var in dist.variables])

    # Check that the distribution passes Variables through to the accessor
    # properties (without converting them to Tensor or anything like that).
    for k, v in six.iteritems(dist.parameters):
      if not tensor_util.is_ref(v):
        continue
      self.assertIs(getattr(dist, k), v)

    # Check that standard statistics do not read distribution parameters more
    # than twice (once in the stat itself and up to once in any validation
    # assertions).
    max_permissible = 2 + extra_tensor_conversions_allowed(dist)
    for stat in sorted(data.draw(
        hps.sets(
            hps.one_of(
                map(hps.just, [
                    'covariance', 'entropy', 'mean', 'mode', 'stddev',
                    'variance'
                ])),
            min_size=3,
            max_size=3))):
      hp.note('Testing excessive var usage in {}.{}'.format(dist_name, stat))
      try:
        with tfp_hps.assert_no_excessive_var_usage(
            'statistic `{}` of `{}`'.format(stat, dist),
            max_permissible=max_permissible):
          getattr(dist, stat)()

      except NotImplementedError:
        pass

    # Check that `sample` doesn't read distribution parameters more than twice,
    # and that it produces non-None gradients (if the distribution is fully
    # reparameterized).
    with tf.GradientTape() as tape:
      # TDs do bijector assertions twice (once by distribution.sample, and once
      # by bijector.forward).
      max_permissible = 2 + extra_tensor_conversions_allowed(dist)
      with tfp_hps.assert_no_excessive_var_usage(
          'method `sample` of `{}`'.format(dist),
          max_permissible=max_permissible):
        sample = dist.sample(seed=seed)
    if dist.reparameterization_type == tfd.FULLY_REPARAMETERIZED:
      grads = tape.gradient(sample, dist.variables)
      for grad, var in zip(grads, dist.variables):
        var_name = var.name.rstrip('_0123456789:')
        if var_name in NO_SAMPLE_PARAM_GRADS.get(dist_name, ()):
          continue
        if grad is None:
          raise AssertionError(
              'Missing sample -> {} grad for distribution {}'.format(
                  var_name, dist_name))

    # Turn off validations, since TODO(b/129271256) log_prob can choke on dist's
    # own samples.  Also, to relax conversion counts for KL (might do >2 w/
    # validate_args).
    dist = dist.copy(validate_args=False)
    dist2 = dist2.copy(validate_args=False)

    # Test that KL divergence reads distribution parameters at most once, and
    # that is produces non-None gradients.
    try:
      for d1, d2 in (dist, dist2), (dist2, dist):
        if dist_name in SKIP_KL_CHECK_DIST_VAR_GRADS:
          continue
        with tf.GradientTape() as tape:
          with tfp_hps.assert_no_excessive_var_usage(
              '`kl_divergence` of (`{}` (vars {}), `{}` (vars {}))'.format(
                  d1, d1.variables, d2, d2.variables),
              max_permissible=1):  # No validation => 1 convert per var.
            kl = d1.kl_divergence(d2)
        wrt_vars = list(d1.variables) + list(d2.variables)
        grads = tape.gradient(kl, wrt_vars)
        for grad, var in zip(grads, wrt_vars):
          if grad is None and dist_name not in NO_KL_PARAM_GRADS:
            raise AssertionError('Missing KL({} || {}) -> {} grad:\n'  # pylint: disable=duplicate-string-formatting-argument
                                 '{} vars: {}\n{} vars: {}'.format(
                                     d1, d2, var, d1, d1.variables, d2,
                                     d2.variables))
    except NotImplementedError:
      # Raised by kl_divergence if no registered KL is found.
      pass

    # Test that log_prob produces non-None gradients, except for distributions
    # on the NO_LOG_PROB_PARAM_GRADS blocklist.
    if dist_name not in NO_LOG_PROB_PARAM_GRADS:
      with tf.GradientTape() as tape:
        lp = dist.log_prob(tf.stop_gradient(sample))
      grads = tape.gradient(lp, dist.variables)
      for grad, var in zip(grads, dist.variables):
        if grad is None:
          raise AssertionError(
              'Missing log_prob -> {} grad for distribution {}'.format(
                  var, dist_name))

    # Test that all forms of probability evaluation avoid reading distribution
    # parameters more than once.
    for evaluative in sorted(data.draw(
        hps.sets(
            hps.one_of(
                map(hps.just, [
                    'log_prob', 'prob', 'log_cdf', 'cdf',
                    'log_survival_function', 'survival_function'
                ])),
            min_size=3,
            max_size=3))):
      hp.note('Testing excessive var usage in {}.{}'.format(
          dist_name, evaluative))
      try:
        # No validation => 1 convert. But for TD we allow 2:
        # dist.log_prob(bijector.inverse(samp)) + bijector.ildj(samp)
        max_permissible = 2 + extra_tensor_conversions_allowed(dist)
        with tfp_hps.assert_no_excessive_var_usage(
            'evaluative `{}` of `{}`'.format(evaluative, dist),
            max_permissible=max_permissible):
          getattr(dist, evaluative)(sample)
      except NotImplementedError:
        pass


class DistributionCompositeTensorTest(test_util.TestCase):

  def _test_sample_and_log_prob(self, dist_name, dist):
    seed = test_util.test_seed(sampler_type='stateless')
    num_samples = 3

    # Sample from the distribution before composite tensoring
    sample1 = self.evaluate(dist.sample(num_samples, seed=seed))
    hp.note('Drew samples {}'.format(sample1))

    # Sample from the distribution after composite tensoring
    composite_dist = experimental.as_composite(dist)
    flat = tf.nest.flatten(composite_dist, expand_composites=True)
    unflat = tf.nest.pack_sequence_as(
        composite_dist, flat, expand_composites=True)
    sample2 = self.evaluate(unflat.sample(num_samples, seed=seed))
    hp.note('Drew samples {}'.format(sample2))

    # Check that the samples are the same
    self.assertAllClose(sample1, sample2)

    # Check that all the log_probs agree for the samples from before ...
    ct_lp1 = unflat.log_prob(sample1)
    orig_lp1 = dist.log_prob(sample1)
    ct_lp1_, orig_lp1_ = self.evaluate((ct_lp1, orig_lp1))
    self.assertAllClose(ct_lp1_, orig_lp1_)

    # ... and after.  (Even though they're supposed to be the same anyway.)
    ct_lp2 = unflat.log_prob(sample2)
    orig_lp2 = dist.log_prob(sample2)
    ct_lp2_, orig_lp2_ = self.evaluate((ct_lp2, orig_lp2))
    self.assertAllClose(ct_lp2_, orig_lp2_)

  # TODO(alexeev): Add coverage for meta distributions, in addition to base
  # distributions.
  @parameterized.named_parameters(
      {'testcase_name': dname, 'dist_name': dname}
      for dname in dhps.TF2_FRIENDLY_DISTS)
  @hp.given(hps.data())
  @tfp_hps.tfp_hp_settings()
  def testCompositeTensor(self, dist_name, data):
    dist = data.draw(
        dhps.distributions(
            dist_name=dist_name, enable_vars=False, validate_args=False))
    self._test_sample_and_log_prob(dist_name, dist)


@test_util.test_graph_mode_only
class DistributionXLATest(test_util.TestCase):

  def _test_sample_and_log_prob(self, dist_name, dist):
    seed = test_util.test_seed(sampler_type='stateless')

    num_samples = 3
    sample = self.evaluate(
        tf.function(experimental_compile=True)(dist.sample)(
            num_samples, seed=seed))
    hp.note('Trying distribution {}'.format(
        self.evaluate_dict(dist.parameters)))
    hp.note('Drew samples {}'.format(sample))

    xla_lp = tf.function(experimental_compile=True)(dist.log_prob)(
        tf.convert_to_tensor(sample))
    graph_lp = dist.log_prob(sample)
    xla_lp_, graph_lp_ = self.evaluate((xla_lp, graph_lp))
    self.assertAllClose(xla_lp_, graph_lp_,
                        atol=XLA_LOGPROB_ATOL[dist_name],
                        rtol=XLA_LOGPROB_RTOL[dist_name])

  @parameterized.named_parameters(
      {'testcase_name': dname, 'dist_name': dname}
      for dname in dhps.TF2_FRIENDLY_DISTS if dname not in XLA_UNFRIENDLY_DISTS)
  @hp.given(hps.data())
  @tfp_hps.tfp_hp_settings()
  def testXLACompile(self, dist_name, data):
    dist = data.draw(dhps.distributions(
        dist_name=dist_name, enable_vars=False,
        validate_args=False))  # TODO(b/142826246): Enable validate_args.
    self._test_sample_and_log_prob(dist_name, dist)


@test_util.test_graph_and_eager_modes
class DistributionsWorkWithAutoVectorizationTest(test_util.TestCase):

  def _test_vectorization(self, dist_name, dist):
    seed = test_util.test_seed()

    # TODO(b/171752261): New stateless samplers don't work with pfor.
    enable_auto_vectorized_sampling = False

    num_samples = 3
    if (not enable_auto_vectorized_sampling or
        dist_name in SAMPLE_AUTOVECTORIZATION_IS_BROKEN):
      sample = self.evaluate(dist.sample(num_samples, seed=seed))
    else:
      sample = self.evaluate(tf.vectorized_map(
          lambda i: dist.sample(seed=seed),
          tf.range(num_samples),
          fallback_to_while_loop=False))
    hp.note('Drew samples {}'.format(sample))

    if dist_name not in LOGPROB_AUTOVECTORIZATION_IS_BROKEN:
      pfor_lp = tf.vectorized_map(
          dist.log_prob,
          tf.convert_to_tensor(sample),
          fallback_to_while_loop=False)
      batch_lp = dist.log_prob(sample)
      pfor_lp_, batch_lp_ = self.evaluate((pfor_lp, batch_lp))
      self.assertAllClose(pfor_lp_, batch_lp_,
                          atol=VECTORIZED_LOGPROB_ATOL[dist_name],
                          rtol=VECTORIZED_LOGPROB_RTOL[dist_name])

  @parameterized.named_parameters(
      {'testcase_name': dname, 'dist_name': dname}
      for dname in sorted(list(dhps.INSTANTIABLE_BASE_DISTS.keys())))
  @hp.given(hps.data())
  @tfp_hps.tfp_hp_settings()
  def testVmap(self, dist_name, data):
    dist = data.draw(dhps.distributions(
        dist_name=dist_name, enable_vars=False,
        validate_args=False))  # TODO(b/142826246): Enable validate_args.
    self._test_vectorization(dist_name, dist)


if __name__ == '__main__':
  # Hypothesis often finds numerical near misses.  Debugging them is much aided
  # by seeing all the digits of every floating point number, instead of the
  # usual default of truncating the printed representation to 8 digits.
  np.set_printoptions(floatmode='unique', precision=None)
  tf.test.main()
