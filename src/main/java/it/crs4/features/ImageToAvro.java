/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2016 CRS4.
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

import java.io.File;

import loci.formats.IFormatReader;
import loci.formats.ImageReader;
import loci.formats.Memoizer;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.ParseException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public final class ImageToAvro {

  private static final Logger LOGGER = LoggerFactory.getLogger(
      ImageToAvro.class);

  private ImageToAvro() {}

  private static CommandLine parseCmdLine(Options opts, String[] args)
      throws ParseException {
    opts.addOption("o", "outdir", true, "write avro files to this dir");
    opts.addOption("t", "tag", true, "base tag for the avro output file");
    opts.addOption("w", "memoWait", true, "Memoizer wait (advanced)");
    opts.addOption("d", "memoDir", true, "Memoizer directory (advanced)");
    CommandLineParser parser = new GnuParser();
    return parser.parse(opts, args);
  }

  public static void main(String[] args) throws Exception {
    Options opts = new Options();
    CommandLine cmd = null;
    try {
      cmd = parseCmdLine(opts, args);
    } catch (ParseException e) {
      System.err.println("ERROR: " + e.getMessage());
      System.exit(1);
    }
    String fn = null;
    try {
      fn = cmd.getArgs()[0];
    } catch (ArrayIndexOutOfBoundsException e) {
      HelpFormatter fmt = new HelpFormatter();
      fmt.printHelp("java ImageToAvro IMG_FILE", opts);
      System.exit(2);
    }
    String outDirName = null;
    if (cmd.hasOption("outdir")) {
      outDirName = cmd.getOptionValue("outdir");
      File outDir = new File(outDirName);
      if (!outDir.exists()) {
        boolean ret = outDir.mkdirs();
        if (!ret) {
          System.err.format("ERROR: can't create %s\n", outDirName);
          System.exit(3);
        }
      }
    }
    String tag = null;
    if (cmd.hasOption("tag")) {
      tag = cmd.getOptionValue("tag");
    } else {
      tag = PathTools.stripext(PathTools.basename(fn));
    }

    long memoWait = 0;
    if (cmd.hasOption("memoWait")) {
      memoWait = Long.parseLong(cmd.getOptionValue("memoWait"));
    }

    String imgPath = (new File(fn)).getAbsolutePath();
    IFormatReader reader = new ImageReader();
    reader.setId(fn);

    File memoDir;
    if (cmd.hasOption("memoDir")) {
      memoDir = new File(cmd.getOptionValue("memoDir"));
      reader = new Memoizer(reader, memoWait, memoDir);
    }

    LOGGER.info("Reading from {}", fn);
    BioImgFactory factory = new BioImgFactory(reader, imgPath);
    int seriesCount = factory.getSeriesCount();

    // FIXME: add support for XY slicing
    String outFn;
    String name;
    for (int i = 0; i < seriesCount; i++) {
      name = String.format("%s_%d", tag, i);
      outFn = new File(outDirName, name + ".avro").getPath();
      factory.setSeries(i);
      factory.writeSeries(name, outFn);
      LOGGER.info("Writing to {}", outFn);
    }
    reader.close();
    LOGGER.info("All done");
  }

}
