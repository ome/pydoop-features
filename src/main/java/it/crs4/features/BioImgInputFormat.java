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
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.JobContext;
import org.apache.hadoop.mapreduce.TaskAttemptContext;
import org.apache.hadoop.mapreduce.RecordReader;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.io.NullWritable;

import org.apache.avro.generic.IndexedRecord;

import loci.formats.ImageReader;
import loci.formats.FormatException;


/**
 * An input format for biomedical images, based upon Bio-Formats.
 */
public class BioImgInputFormat
    extends FileInputFormat<NullWritable, IndexedRecord> {

  private static final Log LOG = LogFactory.getLog(BioImgInputFormat.class);
  public static final String PLANES_PER_MAP = "it.crs4.features.planespermap";

  @Override
  public List<InputSplit> getSplits(JobContext job) throws IOException {
    List<InputSplit> splits = new ArrayList<InputSplit>();
    int planesPerSplit = getPlanesPerSplit(job);
    for (FileStatus status: listStatus(job)) {
      splits.addAll(
          getSplitsForFile(status, job.getConfiguration(), planesPerSplit));
    }
    return splits;
  }

  public static List<FileSplit> getSplitsForFile(
      FileStatus status, Configuration conf, int planesPerSplit
  ) throws IOException {
    List<FileSplit> splits = new ArrayList<FileSplit>();
    Path path = status.getPath();
    // Since it comes from a FileStatus, it's an absolute path
    String absPathName = path.toString();
    FileSystem fs = path.getFileSystem(conf);
    ImageReader reader = new ImageReader();
    try {
      reader.setId(absPathName);
    } catch (FormatException e) {
      throw new RuntimeException("FormatException: " + e.getMessage());
    }
    int nPlanes = reader.getSeriesCount() * reader.getImageCount();
    reader.close();
    LOG.debug(String.format("%s: n. planes = %d", absPathName, nPlanes));
    // FIXME: handle planesPerSplit = 0 (i.e., property not set)
    for (int i = 0; i < nPlanes; i += planesPerSplit) {
      // For now we just hack the default FileSplit
      int len = Math.min(planesPerSplit, nPlanes - i);
      LOG.debug(String.format("adding split: (%d, %d)", i, len));
      splits.add(new FileSplit(path, i, len, new String[] {}));
    }
    return splits;
  }

  @Override
  public RecordReader<NullWritable, IndexedRecord> createRecordReader(
      InputSplit split, TaskAttemptContext context) {
    return new BioImgRecordReader();
  }

  public static void setPlanesPerSplit(JobContext job, int numPlanes) {
    job.getConfiguration().setInt(PLANES_PER_MAP, numPlanes);
  }

  public static int getPlanesPerSplit(JobContext job) {
    return job.getConfiguration().getInt(PLANES_PER_MAP, 0);
  }

}
