/* Copyright 2018 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
=======================================================================*/

// This class has been generated, DO NOT EDIT!

package org.tensorflow.op.data;

import java.util.List;
import org.tensorflow.DataType;
import org.tensorflow.Operand;
import org.tensorflow.Operation;
import org.tensorflow.OperationBuilder;
import org.tensorflow.Output;
import org.tensorflow.ndarray.Shape;
import org.tensorflow.op.RawOp;
import org.tensorflow.op.Scope;
import org.tensorflow.op.annotation.Endpoint;
import org.tensorflow.op.annotation.Operator;
import org.tensorflow.types.TString;
import org.tensorflow.types.family.TType;

/**
 * Creates a dataset that caches elements from `input_dataset`.
 * <p>
 * A CacheDataset will iterate over the input_dataset, and store tensors. If the
 * cache already exists, the cache will be used. If the cache is inappropriate
 * (e.g. cannot be opened, contains tensors of the wrong shape / size), an error
 * will the returned when used.
 */
public final class CacheDataset extends RawOp implements Operand<TType> {
  
  /**
   * Factory method to create a class wrapping a new CacheDataset operation.
   * 
   * @param scope current scope
   * @param inputDataset 
   * @param filename A path on the filesystem where we should cache the dataset. Note: this
   * will be a directory.
   * @param outputTypes 
   * @param outputShapes 
   * @return a new instance of CacheDataset
   */
  @Endpoint(describeByClass = true)
  public static CacheDataset create(Scope scope, Operand<?> inputDataset, Operand<TString> filename, List<DataType<?>> outputTypes, List<Shape> outputShapes) {
    OperationBuilder opBuilder = scope.env().opBuilder("CacheDataset", scope.makeOpName("CacheDataset"));
    opBuilder.addInput(inputDataset.asOutput());
    opBuilder.addInput(filename.asOutput());
    opBuilder = scope.applyControlDependencies(opBuilder);
    DataType[] outputTypesArray = new DataType[outputTypes.size()];
    for (int i = 0; i < outputTypesArray.length; ++i) {
      outputTypesArray[i] = outputTypes.get(i);
    }
    opBuilder.setAttr("output_types", outputTypesArray);
    Shape[] outputShapesArray = new Shape[outputShapes.size()];
    for (int i = 0; i < outputShapesArray.length; ++i) {
      outputShapesArray[i] = outputShapes.get(i);
    }
    opBuilder.setAttr("output_shapes", outputShapesArray);
    return new CacheDataset(opBuilder.build());
  }
  
  /**
   */
  public Output<?> handle() {
    return handle;
  }
  
  @Override
  @SuppressWarnings("unchecked")
  public Output<TType> asOutput() {
    return (Output<TType>) handle;
  }
  
  /** The name of this op, as known by TensorFlow core engine */
  public static final String OP_NAME = "CacheDataset";
  
  private Output<?> handle;
  
  private CacheDataset(Operation operation) {
    super(operation);
    int outputIdx = 0;
    handle = operation.output(outputIdx++);
  }
}