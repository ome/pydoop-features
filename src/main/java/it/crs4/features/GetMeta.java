/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2015-2017 Open Microscopy Environment:
 *   - University of Dundee
 *   - CRS4
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
import java.net.URI;
import java.net.URISyntaxException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.JobContext;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.NLineInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

import loci.formats.ImageReader;
import loci.formats.FormatException;


/**
 * This should evolve into an application that gets all metadata from
 * multiple image files in parallel and writes them in an appropriate
 * format.  For now, it just gets the series and image count (needed
 * by BioImgInputFormat) and writes them out, together with the input
 * path, as tab-separated values.  Expects HDFS paths as input values.
 */
public final class GetMeta {

  private GetMeta() {}

  public static class GetMetaMapper
       extends Mapper<Object, Text, Text, Text> {

    private Text outKey = new Text();
    private Text outValue = new Text();

    private static String getAbsPathName(String fn, Context context)
        throws IOException {
      URI uri = null;
      try {
        uri = new URI(fn);
      } catch (URISyntaxException e) {
        throw new RuntimeException("URISyntaxException: " + e.getMessage());
      }
      if (uri.isAbsolute()) {
        return uri.toString();
      }
      FileSystem fs = FileSystem.get(context.getConfiguration());
      return fs.getFileStatus(new Path(uri)).getPath().toString();
    }

    private static String getMeta(String absPathName) throws IOException {
      ImageReader reader = new ImageReader();
      try {
        reader.setId(absPathName);
      } catch (FormatException e) {
        throw new RuntimeException("FormatException: " + e.getMessage());
      }
      String meta = String.format(
          "%d\t%d", reader.getSeriesCount(), reader.getImageCount());
      reader.close();
      return meta;
    }

    public void map(Object key, Text value, Context context)
        throws IOException, InterruptedException {
      String absPathName = getAbsPathName(value.toString().trim(), context);
      outKey.set(absPathName);
      outValue.set(getMeta(absPathName));
      context.write(outKey, outValue);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    GenericOptionsParser parser = new GenericOptionsParser(conf, args);
    String[] otherArgs = parser.getRemainingArgs();
    if (otherArgs.length < 2) {
      System.err.println("Usage: <prog> IN OUT");
      System.exit(2);
    }
    conf.setInt(JobContext.NUM_REDUCES, 0);
    Job job = Job.getInstance(conf, "get bioimg meta");
    job.setInputFormatClass(NLineInputFormat.class);
    job.setJarByClass(GetMeta.class);
    job.setMapperClass(GetMetaMapper.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    NLineInputFormat.addInputPath(job, new Path(otherArgs[0]));
    FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
