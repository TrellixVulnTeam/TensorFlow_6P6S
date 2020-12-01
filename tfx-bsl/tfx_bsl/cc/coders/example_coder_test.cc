// Copyright 2019 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#include "tfx_bsl/cc/coders/example_coder.h"

#include <memory>

#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "arrow/api.h"
#include "tfx_bsl/cc/util/status.h"
#include "tensorflow/core/example/example.pb.h"
#include "tensorflow/core/example/feature.pb.h"
#include "tensorflow_metadata/proto/v0/schema.pb.h"

namespace tfx_bsl {
namespace {

using ::testing::Test;

std::vector<tensorflow::Example> CreateTestExamples() {
  std::vector<tensorflow::Example> result(4);
  proto2::TextFormat::ParseFromString(
      R"(features {
        feature {
          key: "x"
          value { bytes_list { value: [ "a", "b" ] } }
        }
        feature { key: "y" value { float_list { value: [ 1.0, 2.0 ] } } }
        feature { key: "z" value { int64_list { value: [ 4, 5 ] } } }
      })", &result[0]);
  proto2::TextFormat::ParseFromString(
      R"(features {
        feature { key: "x" value { } }
        feature { key: "y" value { } }
        feature { key: "z" value { } }
      })", &result[1]);
  proto2::TextFormat::ParseFromString(
      R"(features {
        feature { key: "x" value { } }
        feature { key: "y" value { } }
        feature { key: "z" value { } }
      })", &result[2]);
  proto2::TextFormat::ParseFromString(
      R"(features {
        feature { key: "x" value { bytes_list { value: [] } } }
        feature { key: "y" value { float_list { value: [] } } }
        feature { key: "z" value { int64_list { value: [] } } }
      })", &result[3]);
  return result;
}

std::shared_ptr<::arrow::RecordBatch> CreateTestRecordBatch() {
  std::shared_ptr<::arrow::BinaryBuilder> x_values_builder =
      std::make_shared<::arrow::BinaryBuilder>();
  std::shared_ptr<::arrow::FloatBuilder> y_values_builder =
      std::make_shared<::arrow::FloatBuilder>(
          arrow::float32(), arrow::default_memory_pool());
  std::shared_ptr<::arrow::Int64Builder> z_values_builder =
      std::make_shared<::arrow::Int64Builder>(
          arrow::int64(), arrow::default_memory_pool());
  ::arrow::ListBuilder x_builder(
      ::arrow::default_memory_pool(), x_values_builder);
  ::arrow::ListBuilder y_builder(
      ::arrow::default_memory_pool(), y_values_builder);
  ::arrow::ListBuilder z_builder(
      ::arrow::default_memory_pool(), z_values_builder);
  std::shared_ptr<::arrow::Array> x, y, z;
  x_builder.Append().ok();
  x_values_builder->Append("a").ok();
  x_values_builder->Append("b").ok();
  x_builder.AppendNull().ok();
  x_builder.AppendNull().ok();
  x_builder.Append().ok();
  x_builder.Finish(&x).ok();

  y_builder.Append().ok();
  y_values_builder->Append(1.0).ok();
  y_values_builder->Append(2.0).ok();
  y_builder.AppendNull().ok();
  y_builder.AppendNull().ok();
  y_builder.Append().ok();
  y_builder.Finish(&y).ok();

  z_builder.Append().ok();
  z_values_builder->Append(4).ok();
  z_values_builder->Append(5).ok();
  z_builder.AppendNull().ok();
  z_builder.AppendNull().ok();
  z_builder.Append().ok();
  z_builder.Finish(&z).ok();

  std::shared_ptr<::arrow::Schema> schema = ::arrow::schema({
    ::arrow::field("x", ::arrow::list(::arrow::binary())),
    ::arrow::field("y", ::arrow::list(::arrow::float32())),
    ::arrow::field("z", ::arrow::list(::arrow::int64())),
  });

  return ::arrow::RecordBatch::Make(schema, 4, {x, y, z});
}

TEST(ExampleProtoCoderTest, ArrowTableToExampleWorks) {
  std::vector<std::string> serialized_examples;
  std::vector<tensorflow::Example> expected_examples = CreateTestExamples();
  std::shared_ptr<::arrow::RecordBatch> record_batch =
      CreateTestRecordBatch();

  Status status = RecordBatchToExamples(*record_batch, &serialized_examples);
  LOG(INFO) << status;
  ASSERT_TRUE(status.ok());
  std::vector<tensorflow::Example> actual_examples;
  actual_examples.reserve(serialized_examples.size());
  for (const std::string& s : serialized_examples) {
    actual_examples.emplace_back().ParseFromStringPiece(s);
  }
  EXPECT_THAT(actual_examples, testing::ElementsAre(
      testing::EquivToProto(expected_examples[0]),
      testing::EquivToProto(expected_examples[1]),
      testing::EquivToProto(expected_examples[2]),
      testing::EquivToProto(expected_examples[3])));
}

}  // namespace
}  // namespace tfx_bsl
