# Lint as: python3
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test for using the MetricsPlotsAndValidationsWriter API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import string
import tempfile

from absl.testing import parameterized
import apache_beam as beam
from apache_beam.testing import util
import numpy as np
import tensorflow as tf
from tensorflow_model_analysis import config
from tensorflow_model_analysis import constants
from tensorflow_model_analysis import types
from tensorflow_model_analysis.api import model_eval_lib
from tensorflow_model_analysis.eval_saved_model import testutil
from tensorflow_model_analysis.eval_saved_model.example_trainers import fixed_prediction_estimator
from tensorflow_model_analysis.evaluators import legacy_metrics_and_plots_evaluator
from tensorflow_model_analysis.evaluators import metrics_plots_and_validations_evaluator
from tensorflow_model_analysis.extractors import batched_input_extractor
from tensorflow_model_analysis.extractors import batched_predict_extractor_v2
from tensorflow_model_analysis.extractors import legacy_predict_extractor
from tensorflow_model_analysis.extractors import slice_key_extractor
from tensorflow_model_analysis.extractors import unbatch_extractor
from tensorflow_model_analysis.metrics import metric_types
from tensorflow_model_analysis.post_export_metrics import metric_keys
from tensorflow_model_analysis.post_export_metrics import post_export_metrics
from tensorflow_model_analysis.proto import metrics_for_slice_pb2
from tensorflow_model_analysis.proto import validation_result_pb2
from tensorflow_model_analysis.slicer import slicer_lib as slicer
from tensorflow_model_analysis.writers import metrics_plots_and_validations_writer
from tfx_bsl.tfxio import tensor_adapter
from tfx_bsl.tfxio import test_util

from google.protobuf import text_format
from tensorflow_metadata.proto.v0 import schema_pb2


def _make_slice_key(*args):
  if len(args) % 2 != 0:
    raise ValueError('number of arguments should be even')

  result = []
  for i in range(0, len(args), 2):
    result.append((args[i], args[i + 1]))
  result = tuple(result)
  return result


class MetricsPlotsAndValidationsWriterTest(testutil.TensorflowModelAnalysisTest,
                                           parameterized.TestCase):

  def setUp(self):
    super(MetricsPlotsAndValidationsWriterTest, self).setUp()
    self.longMessage = True  # pylint: disable=invalid-name

  def _getTempDir(self):
    return tempfile.mkdtemp()

  def _getExportDir(self):
    return os.path.join(self._getTempDir(), 'export_dir')

  def _getBaselineDir(self):
    return os.path.join(self._getTempDir(), 'baseline_export_dir')

  def _build_keras_model(self, model_dir, mul):
    input_layer = tf.keras.layers.Input(shape=(1,), name='input')
    output_layer = tf.keras.layers.Lambda(
        lambda x, mul: x * mul, output_shape=(1,), arguments={'mul': mul})(
            input_layer)
    model = tf.keras.models.Model([input_layer], output_layer)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(lr=.001),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=['accuracy'])

    model.fit(x=[[0], [1]], y=[[0], [1]], steps_per_epoch=1)
    model.save(model_dir, save_format='tf')
    return self.createTestEvalSharedModel(
        eval_saved_model_path=model_dir, tags=[tf.saved_model.SERVING])

  def testConvertSlicePlotsToProto(self):
    slice_key = _make_slice_key('fruit', 'apple')
    plot_key = metric_types.PlotKey(
        name='calibration_plot', output_name='output_name')
    calibration_plot = text_format.Parse(
        """
        buckets {
          lower_threshold_inclusive: -inf
          upper_threshold_exclusive: 0.0
          num_weighted_examples { value: 0.0 }
          total_weighted_label { value: 0.0 }
          total_weighted_refined_prediction { value: 0.0 }
        }
        buckets {
          lower_threshold_inclusive: 0.0
          upper_threshold_exclusive: 0.5
          num_weighted_examples { value: 1.0 }
          total_weighted_label { value: 1.0 }
          total_weighted_refined_prediction { value: 0.3 }
        }
        buckets {
          lower_threshold_inclusive: 0.5
          upper_threshold_exclusive: 1.0
          num_weighted_examples { value: 1.0 }
          total_weighted_label { value: 0.0 }
          total_weighted_refined_prediction { value: 0.7 }
        }
        buckets {
          lower_threshold_inclusive: 1.0
          upper_threshold_exclusive: inf
          num_weighted_examples { value: 0.0 }
          total_weighted_label { value: 0.0 }
          total_weighted_refined_prediction { value: 0.0 }
        }
     """, metrics_for_slice_pb2.CalibrationHistogramBuckets())

    expected_plots_for_slice = text_format.Parse(
        """
      slice_key {
        single_slice_keys {
          column: 'fruit'
          bytes_value: 'apple'
        }
      }
      plot_keys_and_values {
        key {
          output_name: "output_name"
        }
        value {
          calibration_histogram_buckets {
            buckets {
              lower_threshold_inclusive: -inf
              upper_threshold_exclusive: 0.0
              num_weighted_examples { value: 0.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.0 }
            }
            buckets {
              lower_threshold_inclusive: 0.0
              upper_threshold_exclusive: 0.5
              num_weighted_examples { value: 1.0 }
              total_weighted_label { value: 1.0 }
              total_weighted_refined_prediction { value: 0.3 }
            }
            buckets {
              lower_threshold_inclusive: 0.5
              upper_threshold_exclusive: 1.0
              num_weighted_examples { value: 1.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.7 }
            }
            buckets {
              lower_threshold_inclusive: 1.0
              upper_threshold_exclusive: inf
              num_weighted_examples { value: 0.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.0 }
            }
          }
        }
      }
    """, metrics_for_slice_pb2.PlotsForSlice())

    got = metrics_plots_and_validations_writer.convert_slice_plots_to_proto(
        (slice_key, {
            plot_key: calibration_plot
        }), None)
    self.assertProtoEquals(expected_plots_for_slice, got)

  def testConvertSlicePlotsToProtoLegacyStringKeys(self):
    slice_key = _make_slice_key('fruit', 'apple')
    tfma_plots = {
        metric_keys.CALIBRATION_PLOT_MATRICES:
            np.array([
                [0.0, 0.0, 0.0],
                [0.3, 1.0, 1.0],
                [0.7, 0.0, 1.0],
                [0.0, 0.0, 0.0],
            ]),
        metric_keys.CALIBRATION_PLOT_BOUNDARIES:
            np.array([0.0, 0.5, 1.0]),
    }
    expected_plot_data = """
      slice_key {
        single_slice_keys {
          column: 'fruit'
          bytes_value: 'apple'
        }
      }
      plots {
        key: "post_export_metrics"
        value {
          calibration_histogram_buckets {
            buckets {
              lower_threshold_inclusive: -inf
              upper_threshold_exclusive: 0.0
              num_weighted_examples { value: 0.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.0 }
            }
            buckets {
              lower_threshold_inclusive: 0.0
              upper_threshold_exclusive: 0.5
              num_weighted_examples { value: 1.0 }
              total_weighted_label { value: 1.0 }
              total_weighted_refined_prediction { value: 0.3 }
            }
            buckets {
              lower_threshold_inclusive: 0.5
              upper_threshold_exclusive: 1.0
              num_weighted_examples { value: 1.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.7 }
            }
            buckets {
              lower_threshold_inclusive: 1.0
              upper_threshold_exclusive: inf
              num_weighted_examples { value: 0.0 }
              total_weighted_label { value: 0.0 }
              total_weighted_refined_prediction { value: 0.0 }
            }
          }
        }
      }
    """
    calibration_plot = (
        post_export_metrics.calibration_plot_and_prediction_histogram())
    got = metrics_plots_and_validations_writer.convert_slice_plots_to_proto(
        (slice_key, tfma_plots), [calibration_plot])
    self.assertProtoEquals(expected_plot_data, got)

  def testConvertSlicePlotsToProtoEmptyPlot(self):
    slice_key = _make_slice_key('fruit', 'apple')
    tfma_plots = {metric_keys.ERROR_METRIC: 'error_message'}

    actual_plot = metrics_plots_and_validations_writer.convert_slice_plots_to_proto(
        (slice_key, tfma_plots), [])
    expected_plot = metrics_for_slice_pb2.PlotsForSlice()
    expected_plot.slice_key.CopyFrom(slicer.serialize_slice_key(slice_key))
    expected_plot.plots[
        metric_keys.ERROR_METRIC].debug_message = 'error_message'
    self.assertProtoEquals(expected_plot, actual_plot)

  def testConvertSliceMetricsToProto(self):
    slice_key = _make_slice_key('age', 5, 'language', 'english', 'price', 0.3)
    slice_metrics = {
        metric_types.MetricKey(name='accuracy', output_name='output_name'): 0.8
    }
    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {
          single_slice_keys {
            column: 'age'
            int64_value: 5
          }
          single_slice_keys {
            column: 'language'
            bytes_value: 'english'
          }
          single_slice_keys {
            column: 'price'
            float_value: 0.3
          }
        }
        metric_keys_and_values {
          key {
            name: "accuracy"
            output_name: "output_name"
          }
          value {
            double_value {
              value: 0.8
            }
          }
        }""", metrics_for_slice_pb2.MetricsForSlice())

    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics), None)
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testConvertSliceMetricsToProtoConfusionMatrices(self):
    slice_key = _make_slice_key()

    thresholds = [0.25, 0.75, 1.00]
    matrices = [[0.0, 1.0, 0.0, 2.0, 1.0, 1.0], [1.0, 1.0, 0.0, 1.0, 1.0, 0.5],
                [2.0, 1.0, 0.0, 0.0, float('nan'), 0.0]]

    slice_metrics = {
        metric_keys.CONFUSION_MATRIX_AT_THRESHOLDS_MATRICES: matrices,
        metric_keys.CONFUSION_MATRIX_AT_THRESHOLDS_THRESHOLDS: thresholds,
    }
    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {}
        metrics {
          key: "post_export_metrics/confusion_matrix_at_thresholds"
          value {
            confusion_matrix_at_thresholds {
              matrices {
                threshold: 0.25
                false_negatives: 0.0
                true_negatives: 1.0
                false_positives: 0.0
                true_positives: 2.0
                precision: 1.0
                recall: 1.0
                bounded_false_negatives {
                  value {
                    value: 0.0
                  }
                }
                bounded_true_negatives {
                  value {
                    value: 1.0
                  }
                }
                bounded_true_positives {
                  value {
                    value: 2.0
                  }
                }
                bounded_false_positives {
                  value {
                    value: 0.0
                  }
                }
                bounded_precision {
                  value {
                    value: 1.0
                  }
                }
                bounded_recall {
                  value {
                    value: 1.0
                  }
                }
                t_distribution_false_negatives {
                  unsampled_value {
                    value: 0.0
                  }
                }
                t_distribution_true_negatives {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_true_positives {
                  unsampled_value {
                    value: 2.0
                  }
                }
                t_distribution_false_positives {
                  unsampled_value {
                    value: 0.0
                  }
                }
                t_distribution_precision {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_recall {
                  unsampled_value {
                    value: 1.0
                  }
                }
              }
              matrices {
                threshold: 0.75
                false_negatives: 1.0
                true_negatives: 1.0
                false_positives: 0.0
                true_positives: 1.0
                precision: 1.0
                recall: 0.5
                bounded_false_negatives {
                  value {
                    value: 1.0
                  }
                }
                bounded_true_negatives {
                  value {
                    value: 1.0
                  }
                }
                bounded_true_positives {
                  value {
                    value: 1.0
                  }
                }
                bounded_false_positives {
                  value {
                    value: 0.0
                  }
                }
                bounded_precision {
                  value {
                    value: 1.0
                  }
                }
                bounded_recall {
                  value {
                    value: 0.5
                  }
                }
                t_distribution_false_negatives {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_true_negatives {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_true_positives {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_false_positives {
                  unsampled_value {
                    value: 0.0
                  }
                }
                t_distribution_precision {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_recall {
                  unsampled_value {
                    value: 0.5
                  }
                }
              }
              matrices {
                threshold: 1.00
                false_negatives: 2.0
                true_negatives: 1.0
                false_positives: 0.0
                true_positives: 0.0
                precision: nan
                recall: 0.0
                bounded_false_negatives {
                  value {
                    value: 2.0
                  }
                }
                bounded_true_negatives {
                  value {
                    value: 1.0
                  }
                }
                bounded_true_positives {
                  value {
                    value: 0.0
                  }
                }
                bounded_false_positives {
                  value {
                    value: 0.0
                  }
                }
                bounded_precision {
                  value {
                    value: nan
                  }
                }
                bounded_recall {
                  value {
                    value: 0.0
                  }
                }
                t_distribution_false_negatives {
                  unsampled_value {
                    value: 2.0
                  }
                }
                t_distribution_true_negatives {
                  unsampled_value {
                    value: 1.0
                  }
                }
                t_distribution_true_positives {
                  unsampled_value {
                    value: 0.0
                  }
                }
                t_distribution_false_positives {
                  unsampled_value {
                    value: 0.0
                  }
                }
                t_distribution_precision {
                  unsampled_value {
                    value: nan
                  }
                }
                t_distribution_recall {
                  unsampled_value {
                    value: 0.0
                  }
                }
              }
            }
          }
        }
        """, metrics_for_slice_pb2.MetricsForSlice())

    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics),
        [post_export_metrics.confusion_matrix_at_thresholds(thresholds)])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testConvertSliceMetricsToProtoMetricsRanges(self):
    slice_key = _make_slice_key('age', 5, 'language', 'english', 'price', 0.3)
    slice_metrics = {
        'accuracy': types.ValueWithTDistribution(0.8, 0.1, 9, 0.8),
        metric_keys.AUPRC: 0.1,
        metric_keys.lower_bound_key(metric_keys.AUPRC): 0.05,
        metric_keys.upper_bound_key(metric_keys.AUPRC): 0.17,
        metric_keys.AUC: 0.2,
        metric_keys.lower_bound_key(metric_keys.AUC): 0.1,
        metric_keys.upper_bound_key(metric_keys.AUC): 0.3
    }
    expected_metrics_for_slice = text_format.Parse(
        string.Template("""
        slice_key {
          single_slice_keys {
            column: 'age'
            int64_value: 5
          }
          single_slice_keys {
            column: 'language'
            bytes_value: 'english'
          }
          single_slice_keys {
            column: 'price'
            float_value: 0.3
          }
        }
        metrics {
          key: "accuracy"
          value {
            bounded_value {
              value {
                value: 0.8
              }
              lower_bound {
                value: 0.5737843
              }
              upper_bound {
                value: 1.0262157
              }
              methodology: POISSON_BOOTSTRAP
            }
            confidence_interval {
              lower_bound {
                value: 0.5737843
              }
              upper_bound {
                value: 1.0262157
              }
              t_distribution_value {
                sample_mean {
                  value: 0.8
                }
                sample_standard_deviation {
                  value: 0.1
                }
                sample_degrees_of_freedom {
                  value: 9
                }
                unsampled_value {
                  value: 0.8
                }
              }
            }
          }
        }
        metrics {
          key: "$auc"
          value {
            bounded_value {
              lower_bound {
                value: 0.1
              }
              upper_bound {
                value: 0.3
              }
              value {
                value: 0.2
              }
              methodology: RIEMANN_SUM
            }
          }
        }
        metrics {
          key: "$auprc"
          value {
            bounded_value {
              lower_bound {
                value: 0.05
              }
              upper_bound {
                value: 0.17
              }
              value {
                value: 0.1
              }
              methodology: RIEMANN_SUM
            }
          }
        }""").substitute(auc=metric_keys.AUC, auprc=metric_keys.AUPRC),
        metrics_for_slice_pb2.MetricsForSlice())

    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics),
        [post_export_metrics.auc(),
         post_export_metrics.auc(curve='PR')])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testConvertSliceMetricsToProtoFromLegacyStrings(self):
    slice_key = _make_slice_key('age', 5, 'language', 'english', 'price', 0.3)
    slice_metrics = {
        'accuracy': 0.8,
        metric_keys.AUPRC: 0.1,
        metric_keys.lower_bound_key(metric_keys.AUPRC): 0.05,
        metric_keys.upper_bound_key(metric_keys.AUPRC): 0.17,
        metric_keys.AUC: 0.2,
        metric_keys.lower_bound_key(metric_keys.AUC): 0.1,
        metric_keys.upper_bound_key(metric_keys.AUC): 0.3
    }
    expected_metrics_for_slice = text_format.Parse(
        string.Template("""
        slice_key {
          single_slice_keys {
            column: 'age'
            int64_value: 5
          }
          single_slice_keys {
            column: 'language'
            bytes_value: 'english'
          }
          single_slice_keys {
            column: 'price'
            float_value: 0.3
          }
        }
        metrics {
          key: "accuracy"
          value {
            double_value {
              value: 0.8
            }
          }
        }
        metrics {
          key: "$auc"
          value {
            bounded_value {
              lower_bound {
                value: 0.1
              }
              upper_bound {
                value: 0.3
              }
              value {
                value: 0.2
              }
              methodology: RIEMANN_SUM
            }
          }
        }
        metrics {
          key: "$auprc"
          value {
            bounded_value {
              lower_bound {
                value: 0.05
              }
              upper_bound {
                value: 0.17
              }
              value {
                value: 0.1
              }
              methodology: RIEMANN_SUM
            }
          }
        }""").substitute(auc=metric_keys.AUC, auprc=metric_keys.AUPRC),
        metrics_for_slice_pb2.MetricsForSlice())

    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics),
        [post_export_metrics.auc(),
         post_export_metrics.auc(curve='PR')])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testConvertSliceMetricsToProtoEmptyMetrics(self):
    slice_key = _make_slice_key('age', 5, 'language', 'english', 'price', 0.3)
    slice_metrics = {metric_keys.ERROR_METRIC: 'error_message'}

    actual_metrics = (
        metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
            (slice_key, slice_metrics),
            [post_export_metrics.auc(),
             post_export_metrics.auc(curve='PR')]))

    expected_metrics = metrics_for_slice_pb2.MetricsForSlice()
    expected_metrics.slice_key.CopyFrom(slicer.serialize_slice_key(slice_key))
    expected_metrics.metrics[
        metric_keys.ERROR_METRIC].debug_message = 'error_message'
    self.assertProtoEquals(expected_metrics, actual_metrics)

  def testConvertSliceMetricsToProtoStringMetrics(self):
    slice_key = _make_slice_key()
    slice_metrics = {
        'valid_ascii': b'test string',
        'valid_unicode': b'\xF0\x9F\x90\x84',  # U+1F404, Cow
        'invalid_unicode': b'\xE2\x28\xA1',
    }
    expected_metrics_for_slice = metrics_for_slice_pb2.MetricsForSlice()
    expected_metrics_for_slice.slice_key.SetInParent()
    expected_metrics_for_slice.metrics[
        'valid_ascii'].bytes_value = slice_metrics['valid_ascii']
    expected_metrics_for_slice.metrics[
        'valid_unicode'].bytes_value = slice_metrics['valid_unicode']
    expected_metrics_for_slice.metrics[
        'invalid_unicode'].bytes_value = slice_metrics['invalid_unicode']

    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics), [])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testCombineValidationsValidationOk(self):
    input_validations = [
        text_format.Parse(
            """
            validation_ok: true
            metric_validations_per_slice {
              slice_key  {
                single_slice_keys {
                  column: "x"
                  bytes_value: "x1"
                }
              }
            }
            validation_details {
              slicing_details {
                slicing_spec {}
                num_matching_slices: 1
              }
              slicing_details {
                slicing_spec {
                  feature_keys: ["x", "y"]
                }
                num_matching_slices: 1
              }
            }""", validation_result_pb2.ValidationResult()),
        text_format.Parse(
            """
            validation_ok: true
            validation_details {
              slicing_details {
                slicing_spec {
                  feature_keys: ["x"]
                }
                num_matching_slices: 1
              }
              slicing_details {
                slicing_spec {
                  feature_keys: ["x", "y"]
                }
                num_matching_slices: 2
              }
            }""", validation_result_pb2.ValidationResult())
    ]

    eval_config = config.EvalConfig(
        model_specs=[
            config.ModelSpec(name='candidate'),
            config.ModelSpec(name='baseline', is_baseline=True)
        ],
        slicing_specs=[config.SlicingSpec()],
        metrics_specs=[
            config.MetricsSpec(
                metrics=[
                    config.MetricConfig(
                        class_name='AUC',
                        per_slice_thresholds=[
                            config.PerSliceMetricThreshold(
                                slicing_specs=[config.SlicingSpec()],
                                threshold=config.MetricThreshold(
                                    value_threshold=config
                                    .GenericValueThreshold(
                                        lower_bound={'value': 0.7})))
                        ]),
                ],
                model_names=['candidate', 'baseline']),
        ])

    expected_validation = text_format.Parse(
        """
        validation_ok: true
        metric_validations_per_slice {
          slice_key  {
            single_slice_keys {
              column: "x"
              bytes_value: "x1"
            }
          }
        }
        validation_details {
          slicing_details {
            slicing_spec {}
            num_matching_slices: 1
          }
          slicing_details {
            slicing_spec {
              feature_keys: ["x", "y"]
            }
            num_matching_slices: 3
          }
          slicing_details {
            slicing_spec {
              feature_keys: ["x"]
            }
            num_matching_slices: 1
          }
        }""", validation_result_pb2.ValidationResult())

    def verify_fn(result):
      self.assertLen(result, 1)
      self.assertProtoEquals(expected_validation, result[0])

    with beam.Pipeline() as pipeline:
      result = (
          pipeline
          | 'Create' >> beam.Create(input_validations)
          | 'CombineValidations' >> beam.CombineGlobally(
              metrics_plots_and_validations_writer.CombineValidations(
                  eval_config)))
      util.assert_that(result, verify_fn)

  def testCombineValidationsMissingSlices(self):
    input_validations = [
        text_format.Parse(
            """
            validation_ok: false
            metric_validations_per_slice {
              slice_key  {
                single_slice_keys {
                  column: "x"
                  bytes_value: "x1"
                }
              }
              failures {
                metric_key {
                  name: "auc"
                  model_name: "candidate"
                  is_diff: true
                }
                metric_threshold {
                  value_threshold {
                    lower_bound { value: 0.7 }
                  }
                }
                metric_value {
                  double_value { value: 0.6 }
                }
              }
            }
            validation_details {
              slicing_details {
                slicing_spec {}
                num_matching_slices: 1
              }
              slicing_details {
                slicing_spec {
                  feature_keys: ["x", "y"]
                }
                num_matching_slices: 1
              }
            }""", validation_result_pb2.ValidationResult()),
        text_format.Parse(
            """
            validation_ok: true
            validation_details {
              slicing_details {
                slicing_spec {
                  feature_keys: ["x"]
                }
                num_matching_slices: 1
              }
              slicing_details {
                slicing_spec {
                  feature_keys: ["x", "y"]
                }
                num_matching_slices: 2
              }
            }""", validation_result_pb2.ValidationResult())
    ]

    slicing_specs = [
        config.SlicingSpec(),
        config.SlicingSpec(feature_keys=['x']),
        config.SlicingSpec(feature_keys=['x', 'y']),
        config.SlicingSpec(feature_keys=['z']),
    ]
    eval_config = config.EvalConfig(
        model_specs=[
            config.ModelSpec(name='candidate'),
            config.ModelSpec(name='baseline', is_baseline=True)
        ],
        slicing_specs=slicing_specs,
        metrics_specs=[
            config.MetricsSpec(
                metrics=[
                    config.MetricConfig(
                        class_name='AUC',
                        per_slice_thresholds=[
                            config.PerSliceMetricThreshold(
                                slicing_specs=slicing_specs,
                                threshold=config.MetricThreshold(
                                    value_threshold=config
                                    .GenericValueThreshold(
                                        lower_bound={'value': 0.7})))
                        ]),
                ],
                model_names=['candidate', 'baseline']),
        ])

    expected_validation = text_format.Parse(
        """
        validation_ok: false
        metric_validations_per_slice {
          slice_key  {
            single_slice_keys {
              column: "x"
              bytes_value: "x1"
            }
          }
          failures {
            metric_key {
              name: "auc"
              model_name: "candidate"
              is_diff: true
            }
            metric_threshold {
              value_threshold {
                lower_bound { value: 0.7 }
              }
            }
            metric_value {
              double_value { value: 0.6 }
            }
          }
        }
        missing_slices {
          feature_keys: "z"
        }
        validation_details {
          slicing_details {
            slicing_spec {}
            num_matching_slices: 1
          }
          slicing_details {
            slicing_spec {
              feature_keys: ["x", "y"]
            }
            num_matching_slices: 3
          }
          slicing_details {
            slicing_spec {
              feature_keys: ["x"]
            }
            num_matching_slices: 1
          }
        }""", validation_result_pb2.ValidationResult())

    def verify_fn(result):
      self.assertLen(result, 1)
      self.assertProtoEquals(expected_validation, result[0])

    with beam.Pipeline() as pipeline:
      result = (
          pipeline
          | 'Create' >> beam.Create(input_validations)
          | 'CombineValidations' >> beam.CombineGlobally(
              metrics_plots_and_validations_writer.CombineValidations(
                  eval_config)))
      util.assert_that(result, verify_fn)

  def testUncertaintyValuedMetrics(self):
    slice_key = _make_slice_key()
    slice_metrics = {
        'one_dim':
            types.ValueWithTDistribution(2.0, 1.0, 3, 2.0),
        'nans':
            types.ValueWithTDistribution(
                float('nan'), float('nan'), -1, float('nan')),
    }
    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {}
        metrics {
          key: "one_dim"
          value {
            bounded_value {
              value {
                value: 2.0
              }
              lower_bound {
                value: -1.1824463
              }
              upper_bound {
                value: 5.1824463
              }
              methodology: POISSON_BOOTSTRAP
            }
            confidence_interval {
              lower_bound {
                value: -1.1824463
              }
              upper_bound {
                value: 5.1824463
              }
              t_distribution_value {
                sample_mean {
                  value: 2.0
                }
                sample_standard_deviation {
                  value: 1.0
                }
                sample_degrees_of_freedom {
                  value: 3
                }
                unsampled_value {
                  value: 2.0
                }
              }
            }
          }
        }
        metrics {
          key: "nans"
          value {
            bounded_value {
              value {
                value: nan
              }
              lower_bound {
                value: nan
              }
              upper_bound {
                value: nan
              }
              methodology: POISSON_BOOTSTRAP
            }
            confidence_interval {
              lower_bound {
                value: nan
              }
              upper_bound {
                value: nan
              }
              t_distribution_value {
                sample_mean {
                  value: nan
                }
                sample_standard_deviation {
                  value: nan
                }
                sample_degrees_of_freedom {
                  value: -1
                }
                unsampled_value {
                  value: nan
                }
              }
            }
          }
        }
        """, metrics_for_slice_pb2.MetricsForSlice())
    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics), [])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  def testConvertSliceMetricsToProtoTensorValuedMetrics(self):
    slice_key = _make_slice_key()
    slice_metrics = {
        'one_dim':
            np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32),
        'two_dims':
            np.array([['two', 'dims', 'test'], ['TWO', 'DIMS', 'TEST']]),
        'three_dims':
            np.array([[[100, 200, 300]], [[500, 600, 700]]], dtype=np.int64),
    }
    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {}
        metrics {
          key: "one_dim"
          value {
            array_value {
              data_type: FLOAT32
              shape: 4
              float32_values: [1.0, 2.0, 3.0, 4.0]
            }
          }
        }
        metrics {
          key: "two_dims"
          value {
            array_value {
              data_type: BYTES
              shape: [2, 3]
              bytes_values: ["two", "dims", "test", "TWO", "DIMS", "TEST"]
            }
          }
        }
        metrics {
          key: "three_dims"
          value {
            array_value {
              data_type: INT64
              shape: [2, 1, 3]
              int64_values: [100, 200, 300, 500, 600, 700]
            }
          }
        }
        """, metrics_for_slice_pb2.MetricsForSlice())
    got = metrics_plots_and_validations_writer.convert_slice_metrics_to_proto(
        (slice_key, slice_metrics), [])
    self.assertProtoEquals(expected_metrics_for_slice, got)

  _OUTPUT_FORMAT_PARAMS = [('without_output_file_format', ''),
                           ('tfrecord_file_format', 'tfrecord'),
                           ('parquet_file_format', 'parquet')]

  @parameterized.named_parameters(_OUTPUT_FORMAT_PARAMS)
  def testWriteValidationResults(self, output_file_format):
    model_dir, baseline_dir = self._getExportDir(), self._getBaselineDir()
    eval_shared_model = self._build_keras_model(model_dir, mul=0)
    baseline_eval_shared_model = self._build_keras_model(baseline_dir, mul=1)
    validations_file = os.path.join(self._getTempDir(),
                                    constants.VALIDATIONS_KEY)
    schema = text_format.Parse(
        """
        tensor_representation_group {
          key: ""
          value {
            tensor_representation {
              key: "input"
              value {
                dense_tensor {
                  column_name: "input"
                  shape { dim { size: 1 } }
                }
              }
            }
          }
        }
        feature {
          name: "input"
          type: FLOAT
        }
        feature {
          name: "label"
          type: FLOAT
        }
        feature {
          name: "example_weight"
          type: FLOAT
        }
        feature {
          name: "extra_feature"
          type: BYTES
        }
        """, schema_pb2.Schema())
    tfx_io = test_util.InMemoryTFExampleRecord(
        schema=schema, raw_record_column_name=constants.ARROW_INPUT_COLUMN)
    tensor_adapter_config = tensor_adapter.TensorAdapterConfig(
        arrow_schema=tfx_io.ArrowSchema(),
        tensor_representations=tfx_io.TensorRepresentations())
    examples = [
        self._makeExample(
            input=0.0,
            label=1.0,
            example_weight=1.0,
            extra_feature='non_model_feature'),
        self._makeExample(
            input=1.0,
            label=0.0,
            example_weight=0.5,
            extra_feature='non_model_feature'),
    ]

    slicing_specs = [
        config.SlicingSpec(),
        config.SlicingSpec(feature_keys=['slice_does_not_exist'])
    ]
    eval_config = config.EvalConfig(
        model_specs=[
            config.ModelSpec(
                name='candidate',
                label_key='label',
                example_weight_key='example_weight'),
            config.ModelSpec(
                name='baseline',
                label_key='label',
                example_weight_key='example_weight',
                is_baseline=True)
        ],
        slicing_specs=slicing_specs,
        metrics_specs=[
            config.MetricsSpec(
                metrics=[
                    config.MetricConfig(
                        class_name='WeightedExampleCount',
                        per_slice_thresholds=[
                            config.PerSliceMetricThreshold(
                                slicing_specs=slicing_specs,
                                # 1.5 < 1, NOT OK.
                                threshold=config.MetricThreshold(
                                    value_threshold=config
                                    .GenericValueThreshold(
                                        upper_bound={'value': 1})))
                        ]),
                    config.MetricConfig(
                        class_name='ExampleCount',
                        # 2 > 10, NOT OK.
                        threshold=config.MetricThreshold(
                            value_threshold=config.GenericValueThreshold(
                                lower_bound={'value': 10}))),
                    config.MetricConfig(
                        class_name='MeanLabel',
                        # 0 > 0 and 0 > 0%?: NOT OK.
                        threshold=config.MetricThreshold(
                            change_threshold=config.GenericChangeThreshold(
                                direction=config.MetricDirection
                                .HIGHER_IS_BETTER,
                                relative={'value': 0},
                                absolute={'value': 0}))),
                    config.MetricConfig(
                        # MeanPrediction = (0+0)/(1+0.5) = 0
                        class_name='MeanPrediction',
                        # -.01 < 0 < .01, OK.
                        # Diff% = -.333/.333 = -100% < -99%, OK.
                        # Diff = 0 - .333 = -.333 < 0, OK.
                        threshold=config.MetricThreshold(
                            value_threshold=config.GenericValueThreshold(
                                upper_bound={'value': .01},
                                lower_bound={'value': -.01}),
                            change_threshold=config.GenericChangeThreshold(
                                direction=config.MetricDirection
                                .LOWER_IS_BETTER,
                                relative={'value': -.99},
                                absolute={'value': 0})))
                ],
                model_names=['candidate', 'baseline']),
        ],
        options=config.Options(
            disabled_outputs={'values': ['eval_config.json']}),
    )
    slice_spec = [
        slicer.SingleSliceSpec(spec=s) for s in eval_config.slicing_specs
    ]
    eval_shared_models = {
        'candidate': eval_shared_model,
        'baseline': baseline_eval_shared_model
    }
    extractors = [
        batched_input_extractor.BatchedInputExtractor(eval_config),
        batched_predict_extractor_v2.BatchedPredictExtractor(
            eval_shared_model=eval_shared_models,
            eval_config=eval_config,
            tensor_adapter_config=tensor_adapter_config),
        unbatch_extractor.UnbatchExtractor(),
        slice_key_extractor.SliceKeyExtractor(slice_spec=slice_spec)
    ]
    evaluators = [
        metrics_plots_and_validations_evaluator
        .MetricsPlotsAndValidationsEvaluator(
            eval_config=eval_config, eval_shared_model=eval_shared_models)
    ]
    output_paths = {
        constants.VALIDATIONS_KEY: validations_file,
    }
    writers = [
        metrics_plots_and_validations_writer.MetricsPlotsAndValidationsWriter(
            output_paths,
            eval_config=eval_config,
            add_metrics_callbacks=[],
            output_file_format=output_file_format)
    ]

    with beam.Pipeline() as pipeline:
      # pylint: disable=no-value-for-parameter
      _ = (
          pipeline
          | 'Create' >> beam.Create([e.SerializeToString() for e in examples])
          | 'BatchExamples' >> tfx_io.BeamSource()
          | 'InputsToExtracts' >> model_eval_lib.BatchedInputsToExtracts()
          | 'ExtractEvaluate' >> model_eval_lib.ExtractAndEvaluate(
              extractors=extractors, evaluators=evaluators)
          | 'WriteResults' >> model_eval_lib.WriteResults(writers=writers))
      # pylint: enable=no-value-for-parameter

    validation_result = (
        metrics_plots_and_validations_writer
        .load_and_deserialize_validation_result(
            os.path.dirname(validations_file), output_file_format))

    expected_validations = [
        text_format.Parse(
            """
            metric_key {
              name: "weighted_example_count"
              model_name: "candidate"
            }
            metric_threshold {
              value_threshold {
                upper_bound {
                  value: 1.0
                }
              }
            }
            metric_value {
              double_value {
                value: 1.5
              }
            }
            """, validation_result_pb2.ValidationFailure()),
        text_format.Parse(
            """
            metric_key {
              name: "example_count"
              model_name: "candidate"
            }
            metric_threshold {
              value_threshold {
                lower_bound {
                  value: 10.0
                }
              }
            }
            metric_value {
              double_value {
                value: 2.0
              }
            }
            """, validation_result_pb2.ValidationFailure()),
        text_format.Parse(
            """
            metric_key {
              name: "mean_label"
              model_name: "candidate"
              is_diff: true
            }
            metric_threshold {
              change_threshold {
                absolute {
                  value: 0.0
                }
                relative {
                  value: 0.0
                }
                direction: HIGHER_IS_BETTER
              }
            }
            metric_value {
              double_value {
                value: 0.0
              }
            }
            """, validation_result_pb2.ValidationFailure()),
    ]
    self.assertFalse(validation_result.validation_ok)
    self.assertLen(validation_result.metric_validations_per_slice, 1)
    self.assertCountEqual(
        expected_validations,
        validation_result.metric_validations_per_slice[0].failures)

    expected_missing_slices = [
        config.SlicingSpec(feature_keys=['slice_does_not_exist'])
    ]
    self.assertLen(validation_result.missing_slices, 1)
    self.assertCountEqual(expected_missing_slices,
                          validation_result.missing_slices)

    expected_slicing_details = [
        text_format.Parse(
            """
            slicing_spec {
            }
            num_matching_slices: 1
            """, validation_result_pb2.SlicingDetails()),
    ]
    self.assertLen(validation_result.validation_details.slicing_details, 1)
    self.assertCountEqual(expected_slicing_details,
                          validation_result.validation_details.slicing_details)

  @parameterized.named_parameters(_OUTPUT_FORMAT_PARAMS)
  def testWriteMetricsAndPlots(self, output_file_format):
    metrics_file = os.path.join(self._getTempDir(), 'metrics')
    plots_file = os.path.join(self._getTempDir(), 'plots')
    temp_eval_export_dir = os.path.join(self._getTempDir(), 'eval_export_dir')

    _, eval_export_dir = (
        fixed_prediction_estimator.simple_fixed_prediction_estimator(
            None, temp_eval_export_dir))
    eval_config = config.EvalConfig(
        model_specs=[config.ModelSpec()],
        options=config.Options(
            disabled_outputs={'values': ['eval_config.json']}))
    eval_shared_model = self.createTestEvalSharedModel(
        eval_saved_model_path=eval_export_dir,
        add_metrics_callbacks=[
            post_export_metrics.example_count(),
            post_export_metrics.calibration_plot_and_prediction_histogram(
                num_buckets=2)
        ])
    extractors = [
        legacy_predict_extractor.PredictExtractor(eval_shared_model),
        slice_key_extractor.SliceKeyExtractor()
    ]
    evaluators = [
        legacy_metrics_and_plots_evaluator.MetricsAndPlotsEvaluator(
            eval_shared_model)
    ]
    output_paths = {
        constants.METRICS_KEY: metrics_file,
        constants.PLOTS_KEY: plots_file
    }
    writers = [
        metrics_plots_and_validations_writer.MetricsPlotsAndValidationsWriter(
            output_paths,
            eval_config=eval_config,
            add_metrics_callbacks=eval_shared_model.add_metrics_callbacks,
            output_file_format=output_file_format)
    ]

    with beam.Pipeline() as pipeline:
      example1 = self._makeExample(prediction=0.0, label=1.0)
      example2 = self._makeExample(prediction=1.0, label=1.0)

      # pylint: disable=no-value-for-parameter
      _ = (
          pipeline
          | 'Create' >> beam.Create([
              example1.SerializeToString(),
              example2.SerializeToString(),
          ])
          | 'ExtractEvaluateAndWriteResults' >>
          model_eval_lib.ExtractEvaluateAndWriteResults(
              eval_config=eval_config,
              eval_shared_model=eval_shared_model,
              extractors=extractors,
              evaluators=evaluators,
              writers=writers))
      # pylint: enable=no-value-for-parameter

    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {}
        metrics {
          key: "average_loss"
          value {
            double_value {
              value: 0.5
            }
          }
        }
        metrics {
          key: "post_export_metrics/example_count"
          value {
            double_value {
              value: 2.0
            }
          }
        }
        """, metrics_for_slice_pb2.MetricsForSlice())

    metric_records = list(
        metrics_plots_and_validations_writer.load_and_deserialize_metrics(
            metrics_file, output_file_format))
    self.assertLen(metric_records, 1, 'metrics: %s' % metric_records)
    self.assertProtoEquals(expected_metrics_for_slice, metric_records[0])

    expected_plots_for_slice = text_format.Parse(
        """
      slice_key {}
      plots {
        key: "post_export_metrics"
        value {
          calibration_histogram_buckets {
            buckets {
              lower_threshold_inclusive: -inf
              num_weighted_examples {}
              total_weighted_label {}
              total_weighted_refined_prediction {}
            }
            buckets {
              upper_threshold_exclusive: 0.5
              num_weighted_examples {
                value: 1.0
              }
              total_weighted_label {
                value: 1.0
              }
              total_weighted_refined_prediction {}
            }
            buckets {
              lower_threshold_inclusive: 0.5
              upper_threshold_exclusive: 1.0
              num_weighted_examples {
              }
              total_weighted_label {}
              total_weighted_refined_prediction {}
            }
            buckets {
              lower_threshold_inclusive: 1.0
              upper_threshold_exclusive: inf
              num_weighted_examples {
                value: 1.0
              }
              total_weighted_label {
                value: 1.0
              }
              total_weighted_refined_prediction {
                value: 1.0
              }
            }
         }
        }
      }
    """, metrics_for_slice_pb2.PlotsForSlice())

    plot_records = list(
        metrics_plots_and_validations_writer.load_and_deserialize_plots(
            plots_file, output_file_format))
    self.assertLen(plot_records, 1, 'plots: %s' % plot_records)
    self.assertProtoEquals(expected_plots_for_slice, plot_records[0])

  @parameterized.named_parameters(('parquet_file_format', 'parquet'))
  def testLoadAndDeserializeFilteredMetricsAndPlots(self, output_file_format):
    metrics_file = os.path.join(self._getTempDir(), 'metrics')
    plots_file = os.path.join(self._getTempDir(), 'plots')
    temp_eval_export_dir = os.path.join(self._getTempDir(), 'eval_export_dir')

    _, eval_export_dir = (
        fixed_prediction_estimator.simple_fixed_prediction_estimator(
            None, temp_eval_export_dir))
    eval_config = config.EvalConfig(
        model_specs=[config.ModelSpec()],
        slicing_specs=[
            config.SlicingSpec(),
            config.SlicingSpec(feature_keys=['prediction'])
        ],
        options=config.Options(
            disabled_outputs={'values': ['eval_config.json']}))
    eval_shared_model = self.createTestEvalSharedModel(
        eval_saved_model_path=eval_export_dir,
        add_metrics_callbacks=[
            post_export_metrics.example_count(),
            post_export_metrics.calibration_plot_and_prediction_histogram(
                num_buckets=2)
        ])
    extractors = [
        legacy_predict_extractor.PredictExtractor(eval_shared_model),
        slice_key_extractor.SliceKeyExtractor(
            eval_config=eval_config, materialize=False)
    ]
    evaluators = [
        legacy_metrics_and_plots_evaluator.MetricsAndPlotsEvaluator(
            eval_shared_model)
    ]
    output_paths = {
        constants.METRICS_KEY: metrics_file,
        constants.PLOTS_KEY: plots_file
    }
    writers = [
        metrics_plots_and_validations_writer.MetricsPlotsAndValidationsWriter(
            output_paths,
            eval_config=eval_config,
            add_metrics_callbacks=eval_shared_model.add_metrics_callbacks,
            output_file_format=output_file_format)
    ]

    with beam.Pipeline() as pipeline:
      example1 = self._makeExample(prediction=0.0, label=1.0, country='US')
      example2 = self._makeExample(prediction=1.0, label=1.0, country='CA')

      # pylint: disable=no-value-for-parameter
      _ = (
          pipeline
          | 'Create' >> beam.Create([
              example1.SerializeToString(),
              example2.SerializeToString(),
          ])
          | 'ExtractEvaluateAndWriteResults' >>
          model_eval_lib.ExtractEvaluateAndWriteResults(
              eval_config=eval_config,
              eval_shared_model=eval_shared_model,
              extractors=extractors,
              evaluators=evaluators,
              writers=writers))
      # pylint: enable=no-value-for-parameter

    # only read the metrics with slice keys that match the following spec
    slice_keys_filter = [slicer.SingleSliceSpec(features=[('prediction', 0)])]

    expected_metrics_for_slice = text_format.Parse(
        """
        slice_key {
          single_slice_keys {
            column: "prediction"
            float_value: 0
          }
        }
        metrics {
          key: "average_loss"
          value {
            double_value {
              value: 1.0
            }
          }
        }
        metrics {
          key: "post_export_metrics/example_count"
          value {
            double_value {
              value: 1.0
            }
          }
        }
        """, metrics_for_slice_pb2.MetricsForSlice())

    metric_records = list(
        metrics_plots_and_validations_writer.load_and_deserialize_metrics(
            metrics_file, output_file_format, slice_keys_filter))
    self.assertLen(metric_records, 1, 'metrics: %s' % metric_records)
    self.assertProtoEquals(expected_metrics_for_slice, metric_records[0])

    expected_plots_for_slice = text_format.Parse(
        """
      slice_key {
        single_slice_keys {
          column: "prediction"
          float_value: 0
        }
      }
      plots {
        key: "post_export_metrics"
        value {
          calibration_histogram_buckets {
            buckets {
              lower_threshold_inclusive: -inf
              num_weighted_examples {}
              total_weighted_label {}
              total_weighted_refined_prediction {}
            }
            buckets {
              upper_threshold_exclusive: 0.5
              num_weighted_examples {
                value: 1.0
              }
              total_weighted_label {
                value: 1.0
              }
              total_weighted_refined_prediction {}
            }
            buckets {
              lower_threshold_inclusive: 0.5
              upper_threshold_exclusive: 1.0
              num_weighted_examples {
              }
              total_weighted_label {}
              total_weighted_refined_prediction {}
            }
            buckets {
              lower_threshold_inclusive: 1.0
              upper_threshold_exclusive: inf
              num_weighted_examples {
                value: 0.0
              }
              total_weighted_label {
                value: 0.0
              }
              total_weighted_refined_prediction {
                value: 0.0
              }
            }
         }
        }
      }
    """, metrics_for_slice_pb2.PlotsForSlice())

    plot_records = list(
        metrics_plots_and_validations_writer.load_and_deserialize_plots(
            plots_file, output_file_format, slice_keys_filter))
    self.assertLen(plot_records, 1, 'plots: %s' % plot_records)
    self.assertProtoEquals(expected_plots_for_slice, plot_records[0])


if __name__ == '__main__':
  tf.compat.v1.enable_v2_behavior()
  tf.test.main()
