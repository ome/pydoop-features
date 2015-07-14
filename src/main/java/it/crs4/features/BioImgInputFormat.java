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

import java.net.URI;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.StringTokenizer;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.FSDataInputStream;
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
 *
 * Image files contain one or more series of bidimensional planes.
 * This input format assigns a fixed number of planes (controllable
 * via PLANES_PER_MAP) to each input split (which can possibly span
 * multiple series).
 *
 * Since opening all input files to get the number of series and the
 * number of planes per series can take a long time, this information
 * can be provided as an additional metadata file via META_FN.
 * Currently, this is simply a tab-separated file with three columns:
 * 1. fully qualified image path; 2. number of series; 3. number of
 * planes per series.
 */
public class BioImgInputFormat
    extends FileInputFormat<NullWritable, IndexedRecord> {

  private static final Log LOG = LogFactory.getLog(BioImgInputFormat.class);
  public static final String PLANES_PER_MAP = "it.crs4.features.planespermap";
  public static final String META_FN = "it.crs4.features.metadatafile";

  private Map<String, List<Integer>> metadata;

  private void addMetadataRow(String metadataRow) {
    StringTokenizer tokenizer = new StringTokenizer(metadataRow.trim(), "\t");
    String key = tokenizer.nextToken();
    List<Integer> value = new ArrayList<Integer>();
    while (tokenizer.hasMoreTokens()) {
      value.add(Integer.parseInt(tokenizer.nextToken()));
    }
    metadata.put(key, value);
  }

  private void getMetadata(Configuration conf) throws IOException {
    metadata = new HashMap<String, List<Integer>>();
    String pathName = conf.get(META_FN);
    if (null != pathName) {
      URI uri = URI.create(pathName);
      FileSystem fs = FileSystem.get(uri, conf);
      FSDataInputStream in = fs.open(new Path(uri));
      BufferedReader reader = new BufferedReader(new InputStreamReader(in));
      String line;
      while (true) {
        line = reader.readLine();
        if (null == line) {
          break;
        }
        addMetadataRow(line);
      }
      in.close();
      LOG.debug("Got metadata from " + pathName);
    }
  }

  @Override
  public List<InputSplit> getSplits(JobContext job) throws IOException {
    Configuration conf = job.getConfiguration();
    getMetadata(conf);
    List<InputSplit> splits = new ArrayList<InputSplit>();
    int planesPerSplit = getPlanesPerSplit(job);
    for (FileStatus status: listStatus(job)) {
      splits.addAll(
          getSplitsForFile(status, conf, planesPerSplit));
    }
    return splits;
  }

  public List<FileSplit> getSplitsForFile(
      FileStatus status, Configuration conf, int planesPerSplit
  ) throws IOException {
    List<FileSplit> splits = new ArrayList<FileSplit>();
    int nSeries;
    int planesPerSeries;
    Path path = status.getPath();
    // Since it comes from a FileStatus, it's an absolute path
    String absPathName = path.toString();
    List<Integer> md = metadata.get(absPathName);
    if (null != md) {
      nSeries = md.get(0);
      planesPerSeries = md.get(1);
    } else {
      if (!metadata.isEmpty()) {
        LOG.warn("no metadata for " + absPathName);
      }
      FileSystem fs = path.getFileSystem(conf);
      ImageReader reader = new ImageReader();
      try {
        reader.setId(absPathName);
      } catch (FormatException e) {
        throw new RuntimeException("FormatException: " + e.getMessage());
      }
      nSeries = reader.getSeriesCount();
      planesPerSeries = reader.getImageCount();
      reader.close();
    }
    if (planesPerSplit < 1) {
      planesPerSplit = planesPerSeries;
    }
    int nPlanes = nSeries * planesPerSeries;
    LOG.debug(String.format("%s: n. planes = %d", absPathName, nPlanes));
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

  public static void setMetadataFile(JobContext job, String pathName) {
    job.getConfiguration().set(META_FN, pathName);
  }

  public static String getMetadataFile(JobContext job) {
    return job.getConfiguration().get(META_FN);
  }

}
