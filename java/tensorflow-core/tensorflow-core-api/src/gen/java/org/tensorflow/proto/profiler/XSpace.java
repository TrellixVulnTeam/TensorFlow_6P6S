// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: tensorflow/core/profiler/protobuf/xplane.proto

package org.tensorflow.proto.profiler;

/**
 * <pre>
 * A container of parallel XPlanes, generated by one or more profiling sources.
 * Next ID: 4
 * </pre>
 *
 * Protobuf type {@code tensorflow.profiler.XSpace}
 */
public  final class XSpace extends
    com.google.protobuf.GeneratedMessageV3 implements
    // @@protoc_insertion_point(message_implements:tensorflow.profiler.XSpace)
    XSpaceOrBuilder {
private static final long serialVersionUID = 0L;
  // Use XSpace.newBuilder() to construct.
  private XSpace(com.google.protobuf.GeneratedMessageV3.Builder<?> builder) {
    super(builder);
  }
  private XSpace() {
    planes_ = java.util.Collections.emptyList();
    errors_ = com.google.protobuf.LazyStringArrayList.EMPTY;
    warnings_ = com.google.protobuf.LazyStringArrayList.EMPTY;
  }

  @java.lang.Override
  @SuppressWarnings({"unused"})
  protected java.lang.Object newInstance(
      UnusedPrivateParameter unused) {
    return new XSpace();
  }

  @java.lang.Override
  public final com.google.protobuf.UnknownFieldSet
  getUnknownFields() {
    return this.unknownFields;
  }
  private XSpace(
      com.google.protobuf.CodedInputStream input,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws com.google.protobuf.InvalidProtocolBufferException {
    this();
    if (extensionRegistry == null) {
      throw new java.lang.NullPointerException();
    }
    int mutable_bitField0_ = 0;
    com.google.protobuf.UnknownFieldSet.Builder unknownFields =
        com.google.protobuf.UnknownFieldSet.newBuilder();
    try {
      boolean done = false;
      while (!done) {
        int tag = input.readTag();
        switch (tag) {
          case 0:
            done = true;
            break;
          case 10: {
            if (!((mutable_bitField0_ & 0x00000001) != 0)) {
              planes_ = new java.util.ArrayList<org.tensorflow.proto.profiler.XPlane>();
              mutable_bitField0_ |= 0x00000001;
            }
            planes_.add(
                input.readMessage(org.tensorflow.proto.profiler.XPlane.parser(), extensionRegistry));
            break;
          }
          case 18: {
            java.lang.String s = input.readStringRequireUtf8();
            if (!((mutable_bitField0_ & 0x00000002) != 0)) {
              errors_ = new com.google.protobuf.LazyStringArrayList();
              mutable_bitField0_ |= 0x00000002;
            }
            errors_.add(s);
            break;
          }
          case 26: {
            java.lang.String s = input.readStringRequireUtf8();
            if (!((mutable_bitField0_ & 0x00000004) != 0)) {
              warnings_ = new com.google.protobuf.LazyStringArrayList();
              mutable_bitField0_ |= 0x00000004;
            }
            warnings_.add(s);
            break;
          }
          default: {
            if (!parseUnknownField(
                input, unknownFields, extensionRegistry, tag)) {
              done = true;
            }
            break;
          }
        }
      }
    } catch (com.google.protobuf.InvalidProtocolBufferException e) {
      throw e.setUnfinishedMessage(this);
    } catch (java.io.IOException e) {
      throw new com.google.protobuf.InvalidProtocolBufferException(
          e).setUnfinishedMessage(this);
    } finally {
      if (((mutable_bitField0_ & 0x00000001) != 0)) {
        planes_ = java.util.Collections.unmodifiableList(planes_);
      }
      if (((mutable_bitField0_ & 0x00000002) != 0)) {
        errors_ = errors_.getUnmodifiableView();
      }
      if (((mutable_bitField0_ & 0x00000004) != 0)) {
        warnings_ = warnings_.getUnmodifiableView();
      }
      this.unknownFields = unknownFields.build();
      makeExtensionsImmutable();
    }
  }
  public static final com.google.protobuf.Descriptors.Descriptor
      getDescriptor() {
    return org.tensorflow.proto.profiler.XPlaneProtos.internal_static_tensorflow_profiler_XSpace_descriptor;
  }

  @java.lang.Override
  protected com.google.protobuf.GeneratedMessageV3.FieldAccessorTable
      internalGetFieldAccessorTable() {
    return org.tensorflow.proto.profiler.XPlaneProtos.internal_static_tensorflow_profiler_XSpace_fieldAccessorTable
        .ensureFieldAccessorsInitialized(
            org.tensorflow.proto.profiler.XSpace.class, org.tensorflow.proto.profiler.XSpace.Builder.class);
  }

  public static final int PLANES_FIELD_NUMBER = 1;
  private java.util.List<org.tensorflow.proto.profiler.XPlane> planes_;
  /**
   * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
   */
  public java.util.List<org.tensorflow.proto.profiler.XPlane> getPlanesList() {
    return planes_;
  }
  /**
   * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
   */
  public java.util.List<? extends org.tensorflow.proto.profiler.XPlaneOrBuilder> 
      getPlanesOrBuilderList() {
    return planes_;
  }
  /**
   * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
   */
  public int getPlanesCount() {
    return planes_.size();
  }
  /**
   * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
   */
  public org.tensorflow.proto.profiler.XPlane getPlanes(int index) {
    return planes_.get(index);
  }
  /**
   * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
   */
  public org.tensorflow.proto.profiler.XPlaneOrBuilder getPlanesOrBuilder(
      int index) {
    return planes_.get(index);
  }

  public static final int ERRORS_FIELD_NUMBER = 2;
  private com.google.protobuf.LazyStringList errors_;
  /**
   * <pre>
   * Errors (if any) in the generation of planes.
   * </pre>
   *
   * <code>repeated string errors = 2;</code>
   */
  public com.google.protobuf.ProtocolStringList
      getErrorsList() {
    return errors_;
  }
  /**
   * <pre>
   * Errors (if any) in the generation of planes.
   * </pre>
   *
   * <code>repeated string errors = 2;</code>
   */
  public int getErrorsCount() {
    return errors_.size();
  }
  /**
   * <pre>
   * Errors (if any) in the generation of planes.
   * </pre>
   *
   * <code>repeated string errors = 2;</code>
   */
  public java.lang.String getErrors(int index) {
    return errors_.get(index);
  }
  /**
   * <pre>
   * Errors (if any) in the generation of planes.
   * </pre>
   *
   * <code>repeated string errors = 2;</code>
   */
  public com.google.protobuf.ByteString
      getErrorsBytes(int index) {
    return errors_.getByteString(index);
  }

  public static final int WARNINGS_FIELD_NUMBER = 3;
  private com.google.protobuf.LazyStringList warnings_;
  /**
   * <pre>
   * Warnings (if any) in the generation of planes;
   * </pre>
   *
   * <code>repeated string warnings = 3;</code>
   */
  public com.google.protobuf.ProtocolStringList
      getWarningsList() {
    return warnings_;
  }
  /**
   * <pre>
   * Warnings (if any) in the generation of planes;
   * </pre>
   *
   * <code>repeated string warnings = 3;</code>
   */
  public int getWarningsCount() {
    return warnings_.size();
  }
  /**
   * <pre>
   * Warnings (if any) in the generation of planes;
   * </pre>
   *
   * <code>repeated string warnings = 3;</code>
   */
  public java.lang.String getWarnings(int index) {
    return warnings_.get(index);
  }
  /**
   * <pre>
   * Warnings (if any) in the generation of planes;
   * </pre>
   *
   * <code>repeated string warnings = 3;</code>
   */
  public com.google.protobuf.ByteString
      getWarningsBytes(int index) {
    return warnings_.getByteString(index);
  }

  private byte memoizedIsInitialized = -1;
  @java.lang.Override
  public final boolean isInitialized() {
    byte isInitialized = memoizedIsInitialized;
    if (isInitialized == 1) return true;
    if (isInitialized == 0) return false;

    memoizedIsInitialized = 1;
    return true;
  }

  @java.lang.Override
  public void writeTo(com.google.protobuf.CodedOutputStream output)
                      throws java.io.IOException {
    for (int i = 0; i < planes_.size(); i++) {
      output.writeMessage(1, planes_.get(i));
    }
    for (int i = 0; i < errors_.size(); i++) {
      com.google.protobuf.GeneratedMessageV3.writeString(output, 2, errors_.getRaw(i));
    }
    for (int i = 0; i < warnings_.size(); i++) {
      com.google.protobuf.GeneratedMessageV3.writeString(output, 3, warnings_.getRaw(i));
    }
    unknownFields.writeTo(output);
  }

  @java.lang.Override
  public int getSerializedSize() {
    int size = memoizedSize;
    if (size != -1) return size;

    size = 0;
    for (int i = 0; i < planes_.size(); i++) {
      size += com.google.protobuf.CodedOutputStream
        .computeMessageSize(1, planes_.get(i));
    }
    {
      int dataSize = 0;
      for (int i = 0; i < errors_.size(); i++) {
        dataSize += computeStringSizeNoTag(errors_.getRaw(i));
      }
      size += dataSize;
      size += 1 * getErrorsList().size();
    }
    {
      int dataSize = 0;
      for (int i = 0; i < warnings_.size(); i++) {
        dataSize += computeStringSizeNoTag(warnings_.getRaw(i));
      }
      size += dataSize;
      size += 1 * getWarningsList().size();
    }
    size += unknownFields.getSerializedSize();
    memoizedSize = size;
    return size;
  }

  @java.lang.Override
  public boolean equals(final java.lang.Object obj) {
    if (obj == this) {
     return true;
    }
    if (!(obj instanceof org.tensorflow.proto.profiler.XSpace)) {
      return super.equals(obj);
    }
    org.tensorflow.proto.profiler.XSpace other = (org.tensorflow.proto.profiler.XSpace) obj;

    if (!getPlanesList()
        .equals(other.getPlanesList())) return false;
    if (!getErrorsList()
        .equals(other.getErrorsList())) return false;
    if (!getWarningsList()
        .equals(other.getWarningsList())) return false;
    if (!unknownFields.equals(other.unknownFields)) return false;
    return true;
  }

  @java.lang.Override
  public int hashCode() {
    if (memoizedHashCode != 0) {
      return memoizedHashCode;
    }
    int hash = 41;
    hash = (19 * hash) + getDescriptor().hashCode();
    if (getPlanesCount() > 0) {
      hash = (37 * hash) + PLANES_FIELD_NUMBER;
      hash = (53 * hash) + getPlanesList().hashCode();
    }
    if (getErrorsCount() > 0) {
      hash = (37 * hash) + ERRORS_FIELD_NUMBER;
      hash = (53 * hash) + getErrorsList().hashCode();
    }
    if (getWarningsCount() > 0) {
      hash = (37 * hash) + WARNINGS_FIELD_NUMBER;
      hash = (53 * hash) + getWarningsList().hashCode();
    }
    hash = (29 * hash) + unknownFields.hashCode();
    memoizedHashCode = hash;
    return hash;
  }

  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      java.nio.ByteBuffer data)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      java.nio.ByteBuffer data,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data, extensionRegistry);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      com.google.protobuf.ByteString data)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      com.google.protobuf.ByteString data,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data, extensionRegistry);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(byte[] data)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      byte[] data,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws com.google.protobuf.InvalidProtocolBufferException {
    return PARSER.parseFrom(data, extensionRegistry);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(java.io.InputStream input)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseWithIOException(PARSER, input);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      java.io.InputStream input,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseWithIOException(PARSER, input, extensionRegistry);
  }
  public static org.tensorflow.proto.profiler.XSpace parseDelimitedFrom(java.io.InputStream input)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseDelimitedWithIOException(PARSER, input);
  }
  public static org.tensorflow.proto.profiler.XSpace parseDelimitedFrom(
      java.io.InputStream input,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseDelimitedWithIOException(PARSER, input, extensionRegistry);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      com.google.protobuf.CodedInputStream input)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseWithIOException(PARSER, input);
  }
  public static org.tensorflow.proto.profiler.XSpace parseFrom(
      com.google.protobuf.CodedInputStream input,
      com.google.protobuf.ExtensionRegistryLite extensionRegistry)
      throws java.io.IOException {
    return com.google.protobuf.GeneratedMessageV3
        .parseWithIOException(PARSER, input, extensionRegistry);
  }

  @java.lang.Override
  public Builder newBuilderForType() { return newBuilder(); }
  public static Builder newBuilder() {
    return DEFAULT_INSTANCE.toBuilder();
  }
  public static Builder newBuilder(org.tensorflow.proto.profiler.XSpace prototype) {
    return DEFAULT_INSTANCE.toBuilder().mergeFrom(prototype);
  }
  @java.lang.Override
  public Builder toBuilder() {
    return this == DEFAULT_INSTANCE
        ? new Builder() : new Builder().mergeFrom(this);
  }

  @java.lang.Override
  protected Builder newBuilderForType(
      com.google.protobuf.GeneratedMessageV3.BuilderParent parent) {
    Builder builder = new Builder(parent);
    return builder;
  }
  /**
   * <pre>
   * A container of parallel XPlanes, generated by one or more profiling sources.
   * Next ID: 4
   * </pre>
   *
   * Protobuf type {@code tensorflow.profiler.XSpace}
   */
  public static final class Builder extends
      com.google.protobuf.GeneratedMessageV3.Builder<Builder> implements
      // @@protoc_insertion_point(builder_implements:tensorflow.profiler.XSpace)
      org.tensorflow.proto.profiler.XSpaceOrBuilder {
    public static final com.google.protobuf.Descriptors.Descriptor
        getDescriptor() {
      return org.tensorflow.proto.profiler.XPlaneProtos.internal_static_tensorflow_profiler_XSpace_descriptor;
    }

    @java.lang.Override
    protected com.google.protobuf.GeneratedMessageV3.FieldAccessorTable
        internalGetFieldAccessorTable() {
      return org.tensorflow.proto.profiler.XPlaneProtos.internal_static_tensorflow_profiler_XSpace_fieldAccessorTable
          .ensureFieldAccessorsInitialized(
              org.tensorflow.proto.profiler.XSpace.class, org.tensorflow.proto.profiler.XSpace.Builder.class);
    }

    // Construct using org.tensorflow.proto.profiler.XSpace.newBuilder()
    private Builder() {
      maybeForceBuilderInitialization();
    }

    private Builder(
        com.google.protobuf.GeneratedMessageV3.BuilderParent parent) {
      super(parent);
      maybeForceBuilderInitialization();
    }
    private void maybeForceBuilderInitialization() {
      if (com.google.protobuf.GeneratedMessageV3
              .alwaysUseFieldBuilders) {
        getPlanesFieldBuilder();
      }
    }
    @java.lang.Override
    public Builder clear() {
      super.clear();
      if (planesBuilder_ == null) {
        planes_ = java.util.Collections.emptyList();
        bitField0_ = (bitField0_ & ~0x00000001);
      } else {
        planesBuilder_.clear();
      }
      errors_ = com.google.protobuf.LazyStringArrayList.EMPTY;
      bitField0_ = (bitField0_ & ~0x00000002);
      warnings_ = com.google.protobuf.LazyStringArrayList.EMPTY;
      bitField0_ = (bitField0_ & ~0x00000004);
      return this;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.Descriptor
        getDescriptorForType() {
      return org.tensorflow.proto.profiler.XPlaneProtos.internal_static_tensorflow_profiler_XSpace_descriptor;
    }

    @java.lang.Override
    public org.tensorflow.proto.profiler.XSpace getDefaultInstanceForType() {
      return org.tensorflow.proto.profiler.XSpace.getDefaultInstance();
    }

    @java.lang.Override
    public org.tensorflow.proto.profiler.XSpace build() {
      org.tensorflow.proto.profiler.XSpace result = buildPartial();
      if (!result.isInitialized()) {
        throw newUninitializedMessageException(result);
      }
      return result;
    }

    @java.lang.Override
    public org.tensorflow.proto.profiler.XSpace buildPartial() {
      org.tensorflow.proto.profiler.XSpace result = new org.tensorflow.proto.profiler.XSpace(this);
      int from_bitField0_ = bitField0_;
      if (planesBuilder_ == null) {
        if (((bitField0_ & 0x00000001) != 0)) {
          planes_ = java.util.Collections.unmodifiableList(planes_);
          bitField0_ = (bitField0_ & ~0x00000001);
        }
        result.planes_ = planes_;
      } else {
        result.planes_ = planesBuilder_.build();
      }
      if (((bitField0_ & 0x00000002) != 0)) {
        errors_ = errors_.getUnmodifiableView();
        bitField0_ = (bitField0_ & ~0x00000002);
      }
      result.errors_ = errors_;
      if (((bitField0_ & 0x00000004) != 0)) {
        warnings_ = warnings_.getUnmodifiableView();
        bitField0_ = (bitField0_ & ~0x00000004);
      }
      result.warnings_ = warnings_;
      onBuilt();
      return result;
    }

    @java.lang.Override
    public Builder clone() {
      return super.clone();
    }
    @java.lang.Override
    public Builder setField(
        com.google.protobuf.Descriptors.FieldDescriptor field,
        java.lang.Object value) {
      return super.setField(field, value);
    }
    @java.lang.Override
    public Builder clearField(
        com.google.protobuf.Descriptors.FieldDescriptor field) {
      return super.clearField(field);
    }
    @java.lang.Override
    public Builder clearOneof(
        com.google.protobuf.Descriptors.OneofDescriptor oneof) {
      return super.clearOneof(oneof);
    }
    @java.lang.Override
    public Builder setRepeatedField(
        com.google.protobuf.Descriptors.FieldDescriptor field,
        int index, java.lang.Object value) {
      return super.setRepeatedField(field, index, value);
    }
    @java.lang.Override
    public Builder addRepeatedField(
        com.google.protobuf.Descriptors.FieldDescriptor field,
        java.lang.Object value) {
      return super.addRepeatedField(field, value);
    }
    @java.lang.Override
    public Builder mergeFrom(com.google.protobuf.Message other) {
      if (other instanceof org.tensorflow.proto.profiler.XSpace) {
        return mergeFrom((org.tensorflow.proto.profiler.XSpace)other);
      } else {
        super.mergeFrom(other);
        return this;
      }
    }

    public Builder mergeFrom(org.tensorflow.proto.profiler.XSpace other) {
      if (other == org.tensorflow.proto.profiler.XSpace.getDefaultInstance()) return this;
      if (planesBuilder_ == null) {
        if (!other.planes_.isEmpty()) {
          if (planes_.isEmpty()) {
            planes_ = other.planes_;
            bitField0_ = (bitField0_ & ~0x00000001);
          } else {
            ensurePlanesIsMutable();
            planes_.addAll(other.planes_);
          }
          onChanged();
        }
      } else {
        if (!other.planes_.isEmpty()) {
          if (planesBuilder_.isEmpty()) {
            planesBuilder_.dispose();
            planesBuilder_ = null;
            planes_ = other.planes_;
            bitField0_ = (bitField0_ & ~0x00000001);
            planesBuilder_ = 
              com.google.protobuf.GeneratedMessageV3.alwaysUseFieldBuilders ?
                 getPlanesFieldBuilder() : null;
          } else {
            planesBuilder_.addAllMessages(other.planes_);
          }
        }
      }
      if (!other.errors_.isEmpty()) {
        if (errors_.isEmpty()) {
          errors_ = other.errors_;
          bitField0_ = (bitField0_ & ~0x00000002);
        } else {
          ensureErrorsIsMutable();
          errors_.addAll(other.errors_);
        }
        onChanged();
      }
      if (!other.warnings_.isEmpty()) {
        if (warnings_.isEmpty()) {
          warnings_ = other.warnings_;
          bitField0_ = (bitField0_ & ~0x00000004);
        } else {
          ensureWarningsIsMutable();
          warnings_.addAll(other.warnings_);
        }
        onChanged();
      }
      this.mergeUnknownFields(other.unknownFields);
      onChanged();
      return this;
    }

    @java.lang.Override
    public final boolean isInitialized() {
      return true;
    }

    @java.lang.Override
    public Builder mergeFrom(
        com.google.protobuf.CodedInputStream input,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws java.io.IOException {
      org.tensorflow.proto.profiler.XSpace parsedMessage = null;
      try {
        parsedMessage = PARSER.parsePartialFrom(input, extensionRegistry);
      } catch (com.google.protobuf.InvalidProtocolBufferException e) {
        parsedMessage = (org.tensorflow.proto.profiler.XSpace) e.getUnfinishedMessage();
        throw e.unwrapIOException();
      } finally {
        if (parsedMessage != null) {
          mergeFrom(parsedMessage);
        }
      }
      return this;
    }
    private int bitField0_;

    private java.util.List<org.tensorflow.proto.profiler.XPlane> planes_ =
      java.util.Collections.emptyList();
    private void ensurePlanesIsMutable() {
      if (!((bitField0_ & 0x00000001) != 0)) {
        planes_ = new java.util.ArrayList<org.tensorflow.proto.profiler.XPlane>(planes_);
        bitField0_ |= 0x00000001;
       }
    }

    private com.google.protobuf.RepeatedFieldBuilderV3<
        org.tensorflow.proto.profiler.XPlane, org.tensorflow.proto.profiler.XPlane.Builder, org.tensorflow.proto.profiler.XPlaneOrBuilder> planesBuilder_;

    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public java.util.List<org.tensorflow.proto.profiler.XPlane> getPlanesList() {
      if (planesBuilder_ == null) {
        return java.util.Collections.unmodifiableList(planes_);
      } else {
        return planesBuilder_.getMessageList();
      }
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public int getPlanesCount() {
      if (planesBuilder_ == null) {
        return planes_.size();
      } else {
        return planesBuilder_.getCount();
      }
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public org.tensorflow.proto.profiler.XPlane getPlanes(int index) {
      if (planesBuilder_ == null) {
        return planes_.get(index);
      } else {
        return planesBuilder_.getMessage(index);
      }
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder setPlanes(
        int index, org.tensorflow.proto.profiler.XPlane value) {
      if (planesBuilder_ == null) {
        if (value == null) {
          throw new NullPointerException();
        }
        ensurePlanesIsMutable();
        planes_.set(index, value);
        onChanged();
      } else {
        planesBuilder_.setMessage(index, value);
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder setPlanes(
        int index, org.tensorflow.proto.profiler.XPlane.Builder builderForValue) {
      if (planesBuilder_ == null) {
        ensurePlanesIsMutable();
        planes_.set(index, builderForValue.build());
        onChanged();
      } else {
        planesBuilder_.setMessage(index, builderForValue.build());
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder addPlanes(org.tensorflow.proto.profiler.XPlane value) {
      if (planesBuilder_ == null) {
        if (value == null) {
          throw new NullPointerException();
        }
        ensurePlanesIsMutable();
        planes_.add(value);
        onChanged();
      } else {
        planesBuilder_.addMessage(value);
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder addPlanes(
        int index, org.tensorflow.proto.profiler.XPlane value) {
      if (planesBuilder_ == null) {
        if (value == null) {
          throw new NullPointerException();
        }
        ensurePlanesIsMutable();
        planes_.add(index, value);
        onChanged();
      } else {
        planesBuilder_.addMessage(index, value);
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder addPlanes(
        org.tensorflow.proto.profiler.XPlane.Builder builderForValue) {
      if (planesBuilder_ == null) {
        ensurePlanesIsMutable();
        planes_.add(builderForValue.build());
        onChanged();
      } else {
        planesBuilder_.addMessage(builderForValue.build());
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder addPlanes(
        int index, org.tensorflow.proto.profiler.XPlane.Builder builderForValue) {
      if (planesBuilder_ == null) {
        ensurePlanesIsMutable();
        planes_.add(index, builderForValue.build());
        onChanged();
      } else {
        planesBuilder_.addMessage(index, builderForValue.build());
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder addAllPlanes(
        java.lang.Iterable<? extends org.tensorflow.proto.profiler.XPlane> values) {
      if (planesBuilder_ == null) {
        ensurePlanesIsMutable();
        com.google.protobuf.AbstractMessageLite.Builder.addAll(
            values, planes_);
        onChanged();
      } else {
        planesBuilder_.addAllMessages(values);
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder clearPlanes() {
      if (planesBuilder_ == null) {
        planes_ = java.util.Collections.emptyList();
        bitField0_ = (bitField0_ & ~0x00000001);
        onChanged();
      } else {
        planesBuilder_.clear();
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public Builder removePlanes(int index) {
      if (planesBuilder_ == null) {
        ensurePlanesIsMutable();
        planes_.remove(index);
        onChanged();
      } else {
        planesBuilder_.remove(index);
      }
      return this;
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public org.tensorflow.proto.profiler.XPlane.Builder getPlanesBuilder(
        int index) {
      return getPlanesFieldBuilder().getBuilder(index);
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public org.tensorflow.proto.profiler.XPlaneOrBuilder getPlanesOrBuilder(
        int index) {
      if (planesBuilder_ == null) {
        return planes_.get(index);  } else {
        return planesBuilder_.getMessageOrBuilder(index);
      }
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public java.util.List<? extends org.tensorflow.proto.profiler.XPlaneOrBuilder> 
         getPlanesOrBuilderList() {
      if (planesBuilder_ != null) {
        return planesBuilder_.getMessageOrBuilderList();
      } else {
        return java.util.Collections.unmodifiableList(planes_);
      }
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public org.tensorflow.proto.profiler.XPlane.Builder addPlanesBuilder() {
      return getPlanesFieldBuilder().addBuilder(
          org.tensorflow.proto.profiler.XPlane.getDefaultInstance());
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public org.tensorflow.proto.profiler.XPlane.Builder addPlanesBuilder(
        int index) {
      return getPlanesFieldBuilder().addBuilder(
          index, org.tensorflow.proto.profiler.XPlane.getDefaultInstance());
    }
    /**
     * <code>repeated .tensorflow.profiler.XPlane planes = 1;</code>
     */
    public java.util.List<org.tensorflow.proto.profiler.XPlane.Builder> 
         getPlanesBuilderList() {
      return getPlanesFieldBuilder().getBuilderList();
    }
    private com.google.protobuf.RepeatedFieldBuilderV3<
        org.tensorflow.proto.profiler.XPlane, org.tensorflow.proto.profiler.XPlane.Builder, org.tensorflow.proto.profiler.XPlaneOrBuilder> 
        getPlanesFieldBuilder() {
      if (planesBuilder_ == null) {
        planesBuilder_ = new com.google.protobuf.RepeatedFieldBuilderV3<
            org.tensorflow.proto.profiler.XPlane, org.tensorflow.proto.profiler.XPlane.Builder, org.tensorflow.proto.profiler.XPlaneOrBuilder>(
                planes_,
                ((bitField0_ & 0x00000001) != 0),
                getParentForChildren(),
                isClean());
        planes_ = null;
      }
      return planesBuilder_;
    }

    private com.google.protobuf.LazyStringList errors_ = com.google.protobuf.LazyStringArrayList.EMPTY;
    private void ensureErrorsIsMutable() {
      if (!((bitField0_ & 0x00000002) != 0)) {
        errors_ = new com.google.protobuf.LazyStringArrayList(errors_);
        bitField0_ |= 0x00000002;
       }
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public com.google.protobuf.ProtocolStringList
        getErrorsList() {
      return errors_.getUnmodifiableView();
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public int getErrorsCount() {
      return errors_.size();
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public java.lang.String getErrors(int index) {
      return errors_.get(index);
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public com.google.protobuf.ByteString
        getErrorsBytes(int index) {
      return errors_.getByteString(index);
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public Builder setErrors(
        int index, java.lang.String value) {
      if (value == null) {
    throw new NullPointerException();
  }
  ensureErrorsIsMutable();
      errors_.set(index, value);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public Builder addErrors(
        java.lang.String value) {
      if (value == null) {
    throw new NullPointerException();
  }
  ensureErrorsIsMutable();
      errors_.add(value);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public Builder addAllErrors(
        java.lang.Iterable<java.lang.String> values) {
      ensureErrorsIsMutable();
      com.google.protobuf.AbstractMessageLite.Builder.addAll(
          values, errors_);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public Builder clearErrors() {
      errors_ = com.google.protobuf.LazyStringArrayList.EMPTY;
      bitField0_ = (bitField0_ & ~0x00000002);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Errors (if any) in the generation of planes.
     * </pre>
     *
     * <code>repeated string errors = 2;</code>
     */
    public Builder addErrorsBytes(
        com.google.protobuf.ByteString value) {
      if (value == null) {
    throw new NullPointerException();
  }
  checkByteStringIsUtf8(value);
      ensureErrorsIsMutable();
      errors_.add(value);
      onChanged();
      return this;
    }

    private com.google.protobuf.LazyStringList warnings_ = com.google.protobuf.LazyStringArrayList.EMPTY;
    private void ensureWarningsIsMutable() {
      if (!((bitField0_ & 0x00000004) != 0)) {
        warnings_ = new com.google.protobuf.LazyStringArrayList(warnings_);
        bitField0_ |= 0x00000004;
       }
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public com.google.protobuf.ProtocolStringList
        getWarningsList() {
      return warnings_.getUnmodifiableView();
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public int getWarningsCount() {
      return warnings_.size();
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public java.lang.String getWarnings(int index) {
      return warnings_.get(index);
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public com.google.protobuf.ByteString
        getWarningsBytes(int index) {
      return warnings_.getByteString(index);
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public Builder setWarnings(
        int index, java.lang.String value) {
      if (value == null) {
    throw new NullPointerException();
  }
  ensureWarningsIsMutable();
      warnings_.set(index, value);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public Builder addWarnings(
        java.lang.String value) {
      if (value == null) {
    throw new NullPointerException();
  }
  ensureWarningsIsMutable();
      warnings_.add(value);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public Builder addAllWarnings(
        java.lang.Iterable<java.lang.String> values) {
      ensureWarningsIsMutable();
      com.google.protobuf.AbstractMessageLite.Builder.addAll(
          values, warnings_);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public Builder clearWarnings() {
      warnings_ = com.google.protobuf.LazyStringArrayList.EMPTY;
      bitField0_ = (bitField0_ & ~0x00000004);
      onChanged();
      return this;
    }
    /**
     * <pre>
     * Warnings (if any) in the generation of planes;
     * </pre>
     *
     * <code>repeated string warnings = 3;</code>
     */
    public Builder addWarningsBytes(
        com.google.protobuf.ByteString value) {
      if (value == null) {
    throw new NullPointerException();
  }
  checkByteStringIsUtf8(value);
      ensureWarningsIsMutable();
      warnings_.add(value);
      onChanged();
      return this;
    }
    @java.lang.Override
    public final Builder setUnknownFields(
        final com.google.protobuf.UnknownFieldSet unknownFields) {
      return super.setUnknownFields(unknownFields);
    }

    @java.lang.Override
    public final Builder mergeUnknownFields(
        final com.google.protobuf.UnknownFieldSet unknownFields) {
      return super.mergeUnknownFields(unknownFields);
    }


    // @@protoc_insertion_point(builder_scope:tensorflow.profiler.XSpace)
  }

  // @@protoc_insertion_point(class_scope:tensorflow.profiler.XSpace)
  private static final org.tensorflow.proto.profiler.XSpace DEFAULT_INSTANCE;
  static {
    DEFAULT_INSTANCE = new org.tensorflow.proto.profiler.XSpace();
  }

  public static org.tensorflow.proto.profiler.XSpace getDefaultInstance() {
    return DEFAULT_INSTANCE;
  }

  private static final com.google.protobuf.Parser<XSpace>
      PARSER = new com.google.protobuf.AbstractParser<XSpace>() {
    @java.lang.Override
    public XSpace parsePartialFrom(
        com.google.protobuf.CodedInputStream input,
        com.google.protobuf.ExtensionRegistryLite extensionRegistry)
        throws com.google.protobuf.InvalidProtocolBufferException {
      return new XSpace(input, extensionRegistry);
    }
  };

  public static com.google.protobuf.Parser<XSpace> parser() {
    return PARSER;
  }

  @java.lang.Override
  public com.google.protobuf.Parser<XSpace> getParserForType() {
    return PARSER;
  }

  @java.lang.Override
  public org.tensorflow.proto.profiler.XSpace getDefaultInstanceForType() {
    return DEFAULT_INSTANCE;
  }

}
