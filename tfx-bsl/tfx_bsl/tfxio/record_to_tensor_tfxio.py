# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""RecordToTensorTFXIO."""

import copy
from typing import List, Iterator, Optional, Text, Union

import apache_beam as beam
import pyarrow as pa
import tensorflow as tf
from tfx_bsl.coders import batch_util
from tfx_bsl.coders import tf_graph_record_decoder
from tfx_bsl.tfxio import dataset_options
from tfx_bsl.tfxio import dataset_util
from tfx_bsl.tfxio import record_based_tfxio
from tfx_bsl.tfxio import tensor_adapter
from tfx_bsl.tfxio import tensor_to_arrow
from tfx_bsl.tfxio import tfxio


class _RecordToTensorTFXIO(record_based_tfxio.RecordBasedTFXIO):
  """Base class for TFXIO implementations that uses TFGraphRecordDecoder."""

  def __init__(self,
               saved_decoder_path: Text,
               telemetry_descriptors: List[Text],
               physical_format: Text,
               raw_record_column_name: Optional[Text]):

    super().__init__(
        telemetry_descriptors,
        logical_format="tensor",
        physical_format=physical_format,
        raw_record_column_name=raw_record_column_name)
    self._saved_decoder_path = saved_decoder_path
    decoder = tf_graph_record_decoder.load_decoder(saved_decoder_path)
    tensor_to_arrow_converter = tensor_to_arrow.TensorsToRecordBatchConverter(
        decoder.output_type_specs())

    self._arrow_schema_no_raw_record_column = (
        tensor_to_arrow_converter.arrow_schema())
    self._tensor_representations = (
        tensor_to_arrow_converter.tensor_representations())

    self._record_index_column_name = None
    record_index_tensor_name = decoder.record_index_tensor_name
    if record_index_tensor_name is not None:
      record_index_tensor_rep = self._tensor_representations[
          record_index_tensor_name]
      if record_index_tensor_rep.HasField("ragged_tensor"):
        assert len(record_index_tensor_rep.ragged_tensor.feature_path.step) == 1
        self._record_index_column_name = (
            record_index_tensor_rep.ragged_tensor.feature_path.step[0])
      elif record_index_tensor_rep.HasField("varlen_sparse_tensor"):
        self._record_index_column_name = (
            record_index_tensor_rep.varlen_sparse_tensor.column_name)
      else:
        raise ValueError("The record index tensor must be a RaggedTensor or a "
                         "VarLenSparseTensor, but got: {}"
                         .format(record_index_tensor_rep))

    if raw_record_column_name in self._arrow_schema_no_raw_record_column.names:
      raise ValueError("raw record column name: {} collided with an existing "
                       "column.".format(raw_record_column_name))

  def SupportAttachingRawRecords(self) -> bool:
    return True

  def TensorRepresentations(self) -> tensor_adapter.TensorRepresentations:
    return self._tensor_representations

  def _RawRecordToRecordBatchInternal(
      self, batch_size: Optional[int]) -> beam.PTransform:

    @beam.typehints.with_input_types(bytes)
    @beam.typehints.with_output_types(pa.RecordBatch)
    def _PTransformFn(raw_records_pcoll: beam.pvalue.PCollection):
      return (
          raw_records_pcoll
          | "BatchElements" >> beam.BatchElements(
              **batch_util.GetBatchElementsKwargs(batch_size))
          | "Decode" >> beam.ParDo(_RecordsToRecordBatch(
              self._saved_decoder_path, self.raw_record_column_name,
              self._record_index_column_name)))

    return beam.ptransform_fn(_PTransformFn)()

  def _ArrowSchemaNoRawRecordColumn(self) -> pa.Schema:
    return self._arrow_schema_no_raw_record_column

  def _ProjectImpl(self, tensor_names: List[Text]) -> tfxio.TFXIO:
    # We could do better by plumbing the information back to the decoder.
    self_copy = copy.copy(self)
    self_copy._tensor_representations = {  # pylint: disable=protected-access
        k: v
        for k, v in self._tensor_representations.items()
        if k in set(tensor_names)
    }
    return self_copy


class BeamRecordToTensorTFXIO(_RecordToTensorTFXIO):
  """TFXIO implementation that decodes records in pcoll[bytes] with TF Graph."""

  def _RawRecordBeamSourceInternal(self) -> beam.PTransform:
    return (beam.ptransform_fn(lambda x: x)()
            .with_input_types(bytes)
            .with_output_types(bytes))

  def TensorFlowDataset(
      self,
      options: dataset_options.TensorFlowDatasetOptions) -> tf.data.Dataset:
    raise NotImplementedError


class TFRecordToTensorTFXIO(_RecordToTensorTFXIO):
  """Uses a TfGraphRecordDecoder to decode records on TFRecord files.

  This TFXIO assumes the data records are stored in TFRecord and takes a user
  provided TF-graph-based decoder (see tfx_bsl.coders.tf_graph_record_decoder)
  that decodes the records to TF (composite) tensors. The RecordBatches yielded
  by this TFXIO is converted from those tensors, and it's guaranteed that the
  TensorAdapter created by this TFXIO will be able to turn those RecordBatches
  to tensors identical to the TF-graph-based decoder's output.
  """

  def __init__(self,
               file_pattern: Union[List[Text], Text],
               saved_decoder_path: Text,
               telemetry_descriptors: List[Text],
               raw_record_column_name: Optional[Text] = None):
    """Initializer.

    Args:
      file_pattern: One or a list of glob patterns. If a list, must not be
        empty.
      saved_decoder_path: The path to the saved TfGraphRecordDecoder to be
        used for decoding the records. Note that this path must be accessible
        by beam workers.
      telemetry_descriptors: A set of descriptors that identify the component
        that is instantiating this TFXIO. These will be used to construct the
        namespace to contain metrics for profiling and are therefore expected to
        be identifiers of the component itself and not individual instances of
        source use.
      raw_record_column_name: If not None, the generated Arrow RecordBatches
        will contain a column of the given name that contains serialized
        records.
    """
    super().__init__(
        saved_decoder_path,
        telemetry_descriptors,
        physical_format="tfrecords_gzip",
        raw_record_column_name=raw_record_column_name)
    if not isinstance(file_pattern, list):
      file_pattern = [file_pattern]
    assert file_pattern, "Must provide at least one file pattern."
    self._file_pattern = file_pattern

  def _RawRecordBeamSourceInternal(self) -> beam.PTransform:
    return record_based_tfxio.ReadTfRecord(self._file_pattern)

  def RecordBatches(self, options: dataset_options.RecordBatchesOptions):
    raise NotImplementedError

  def TensorFlowDataset(
      self,
      options: dataset_options.TensorFlowDatasetOptions) -> tf.data.Dataset:
    """Creates a TFRecordDataset that yields Tensors.

    The records are parsed by the decoder to create Tensors. This implementation
    is based on tf.data.experimental.ops.make_tf_record_dataset().

    See base class (tfxio.TFXIO) for more details.

    Args:
      options: an options object for the tf.data.Dataset. See
        `dataset_options.TensorFlowDatasetOptions` for more details.
        options.batch_size is the batch size of the input records, but if the
        input record and the output batched tensors by the decoder are not
        batch-aligned (i.e. 1 input record results in 1 "row" in the output
        tensors), then the output may not be of the given batch size. Use
        dataset.unbatch().batch(desired_batch_size) to force the output batch
        size.

    Returns:
      A dataset of `dict` elements, (or a tuple of `dict` elements and label).
      Each `dict` maps feature keys to `Tensor`, `SparseTensor`, or
      `RaggedTensor` objects.

    Raises:
      ValueError: if label_key in the dataset option is not in the arrow schema.
    """
    dataset = dataset_util.make_tf_record_dataset(
        self._file_pattern, options.batch_size, options.drop_final_batch,
        options.num_epochs, options.shuffle, options.shuffle_buffer_size,
        options.shuffle_seed)

    decoder = tf_graph_record_decoder.load_decoder(self._saved_decoder_path)
    def _ParseFn(record):
      # TODO(andylou): Change this once we plumb the projected columns into the
      # decoder itself.
      tensors_dict = decoder.decode_record(record)
      return {
          k: v
          for k, v in tensors_dict.items()
          if k in self._tensor_representations
      }
    dataset = dataset.map(_ParseFn)

    label_key = options.label_key
    if label_key is not None:
      if label_key not in self.TensorRepresentations():
        raise ValueError(
            "The `label_key` provided ({}) must be one of the following tensors"
            "names: {}.".format(label_key, self.TensorRepresentations().keys()))
      dataset = dataset.map(lambda x: (x, x.pop(label_key)))

    return dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)


@beam.typehints.with_input_types(List[bytes])
@beam.typehints.with_output_types(pa.RecordBatch)
class _RecordsToRecordBatch(beam.DoFn):
  """DoFn to convert raw records to RecordBatches."""

  def __init__(self, saved_decoder_path: Text,
               raw_record_column_name: Optional[Text],
               record_index_column_name: Optional[Text]):
    super().__init__()
    self._saved_decoder_path = saved_decoder_path
    self._raw_record_column_name = raw_record_column_name
    self._record_index_column_name = record_index_column_name

    self._tensors_to_record_batch_converter = None
    self._decode_fn = None

  def setup(self):
    decoder = tf_graph_record_decoder.load_decoder(
        self._saved_decoder_path)
    self._tensors_to_record_batch_converter = (
        tensor_to_arrow.TensorsToRecordBatchConverter(
            decoder.output_type_specs()))
    # Store the concrete function to avoid tracing upon calling.
    self._decode_fn = decoder.decode_record.get_concrete_function()

  def process(self, records: List[bytes]) -> Iterator[pa.RecordBatch]:
    # The concrete function only accepts Tensors, so tf.convert_to_tensor
    # is needed.
    decoded = self._tensors_to_record_batch_converter.convert(
        self._decode_fn(tf.convert_to_tensor(records, dtype=tf.string)))
    if self._raw_record_column_name is None:
      yield decoded
    else:
      yield record_based_tfxio.AppendRawRecordColumn(
          decoded, self._raw_record_column_name, records,
          self._record_index_column_name)
