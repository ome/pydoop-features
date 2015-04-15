/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2015 CRS4.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy
 * of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 *
 * END_COPYRIGHT
 */

package it.crs4.features;

import java.io.IOException;

import org.apache.commons.logging.LogFactory;
import org.apache.commons.logging.Log;

import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.RecordReader;
import org.apache.hadoop.mapreduce.TaskAttemptContext;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;

import org.apache.avro.generic.IndexedRecord;

import loci.formats.ImageReader;
import loci.formats.FormatException;


// Everything is based on the one-split-per-series assumption
public class BioImgRecordReader
    extends RecordReader<NullWritable, IndexedRecord> {

  private static final Log LOG = LogFactory.getLog(BioImgRecordReader.class);

  private ImageReader reader;
  private BioImgFactory factory;
  private int seriesIdx;
  private int planeIdx;
  private int nPlanes;
  private String name;
  private IndexedRecord value;

  public void initialize(InputSplit genericSplit, TaskAttemptContext context)
    throws IOException {
    FileSplit split = (FileSplit) genericSplit;
    seriesIdx = (int) split.getStart();
    assert split.getLength() == 1;
    Path file = split.getPath();
    FileSystem fs = file.getFileSystem(context.getConfiguration());
    String absPathName = fs.getFileStatus(file).getPath().toString();
    reader = new ImageReader();
    try {
      reader.setId(absPathName);
    } catch (FormatException e) {
      throw new RuntimeException("FormatException: " + e.getMessage());
    }
    nPlanes = reader.getImageCount();
    reader.setSeries(seriesIdx);
    factory = new BioImgFactory(reader);
    name = PathTools.stripext(PathTools.basename(absPathName));
    planeIdx = 0;
  }

  public boolean nextKeyValue() throws IOException {
    // TODO: support x/y slicing
    try {
      value = factory.build(String.format("%s_%d", name, seriesIdx), planeIdx);
    } catch (FormatException e) {
      throw new RuntimeException("FormatException: " + e.getMessage());
    }
    planeIdx++;
    if (planeIdx >= nPlanes) {
      value = null;
      return false;
    } else {
      return true;
    }
  }

  @Override
  public NullWritable getCurrentKey() {
    return NullWritable.get();
  }

  @Override
  public IndexedRecord getCurrentValue() {
    return value;
  }

  public float getProgress() throws IOException {
    return Math.min(1.0f, (planeIdx + 1) / (float) nPlanes);
  }

  public synchronized void close() throws IOException {
      if (reader != null) {
        reader.close();
      }
    }
}
