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


public final class ImageToAvro {

  private static final Logger LOGGER = LoggerFactory.getLogger(
      ImageToAvro.class);

  private ImageToAvro() {}

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      System.err.println("Usage: java ImageToAvro IMG_FILE");
      return;
    }
    String fn = args[0];
    String name = PathTools.stripext(PathTools.basename(fn));

    ImageReader reader = new ImageReader();
    reader.setId(fn);
    LOGGER.info("Reading from {}", fn);
    int seriesCount = reader.getSeriesCount();
    BioImgFactory factory = new BioImgFactory(reader);

    // FIXME: add support for XY slicing
    String seriesName;
    String outFn;
    for (int i = 0; i < seriesCount; i++) {
      if (seriesCount <= 1) {
        seriesName = name;
      } else {
        seriesName = String.format("%s_%d", name, i);
      }
      outFn = seriesName + ".avro";
      factory.writeSeries(i, seriesName, outFn);
      LOGGER.info("Writing to {}", outFn);
    }
    reader.close();
    LOGGER.info("All done");
  }

}
