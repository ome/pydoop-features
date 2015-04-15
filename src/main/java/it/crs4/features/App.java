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

import loci.formats.ImageReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public final class App {

  private static final Logger LOGGER = LoggerFactory.getLogger(App.class);

  private App() {}

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      System.err.println("Usage: java App IMG_FILE");
      return;
    }
    String fn = args[0];
    String name = PathTools.stripext(PathTools.basename(fn));
    String outFn = name + ".avro";

    ImageReader reader = new ImageReader();
    reader.setId(fn);
    LOGGER.info("Reading from {}", fn);
    int seriesCount = reader.getSeriesCount();
    if (seriesCount != 1) {
      throw new RuntimeException("Multi-series img not supported");
    }
    if (reader.isRGB()) {
      throw new RuntimeException("RGB img not supported");
    }
    if (reader.isInterleaved()) {
      throw new RuntimeException("Interleaving not supported");
    }
    BioImgFactory factory = new BioImgFactory(reader);
    // FIXME: add support for XY slicing
    factory.writeSeries(0, name, outFn);
    LOGGER.info("Writing to {}", outFn);
    reader.close();
    LOGGER.info("All done");
  }

}
