/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2017 Open Microscopy Environment:
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


import java.io.FileReader;
import java.util.List;
import java.util.ArrayList;

import loci.formats.FormatTools;
import loci.formats.MetadataTools;
import loci.formats.IFormatWriter;
import loci.formats.ImageWriter;
import loci.formats.ImageReader;
import loci.formats.meta.IMetadata;
import loci.common.services.ServiceFactory;
import loci.formats.services.OMEXMLService;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.ParseException;


/**
 * Some image analysis data consist of multiple sets, where each file
 * in a set corresponds to a different view (e.g., under different
 * fluorescent stains) of the same object(s).  This utility merges all
 * images from all sets in a single multidimensional file, where each
 * Z index corresponds to a set and each C index to an image in the
 * set.  Assumes single-plane non-RGB images.  Expects a tab-separated
 * input file where each row corresponds to a set and each column to a
 * channel.
 */
public final class MergeImgSets {

  private static final Logger LOGGER = LoggerFactory.getLogger(
    MergeImgSets.class);

  private MergeImgSets() {}

  private static List<List<String>> getFilesets(String setsFn)
      throws Exception {
    FileReader in = new FileReader(setsFn);
    CSVReader reader = new CSVReader(in, "\t");
    List<List<String>> filesets = new ArrayList<List<String>>();
    List<String> row;
    while (true) {
      row = reader.getRow();
      if (null == row) {
        break;
      }
      filesets.add(row);
    }
    reader.close();
    return filesets;
  }

  private static void write(
      List<List<String>> filesets, String outFn, int replication)
      throws Exception {
    ImageReader reader = new ImageReader();
    reader.setId(filesets.get(0).get(0));
    ServiceFactory factory = new ServiceFactory();
    OMEXMLService service = factory.getInstance(OMEXMLService.class);
    IMetadata meta = service.createOMEXMLMetadata();
    int sizeZ = filesets.size();
    if (replication > 1) {
      sizeZ *= replication;
    }
    MetadataTools.populateMetadata(
        meta,
        0,  // n.series
        null,  // img name
        reader.isLittleEndian(),
        "XYCZT",  // dim order
        FormatTools.getPixelTypeString(reader.getPixelType()),
        reader.getSizeX(),
        reader.getSizeY(),
        sizeZ,
        filesets.get(0).size(),  // sizeC
        1,  // sizeT
        1  // samples per pixels -- assumes input images are not RGB
    );
    reader.close();
    IFormatWriter writer = new ImageWriter();
    writer.setMetadataRetrieve(meta);
    writer.setId(outFn);
    writer.setSeries(0);
    int planeCount = 0;
    for (List<String> s: filesets) {
      List<byte[]> planes = new ArrayList<byte[]>();
      for (String fn: s) {
        reader = new ImageReader();
        reader.setId(fn);
        assert (1 == reader.getSeriesCount());
        assert (1 == reader.getImageCount());
        planes.add(reader.openBytes(0));
        reader.close();
      }
      for (int i = 0; i < replication; i++) {
        if (replication > 1) {
          LOGGER.info("replica #" + (i+1));
        }
        for (byte[] p: planes) {
          writer.saveBytes(planeCount, p);
          planeCount++;
        }
      }
    }
    writer.close();
  }

  private static CommandLine parseCmdLine(Options opts, String[] args)
      throws ParseException {
    opts.addOption("r", "replication", true, "n. replicas for each image set");
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
    String[] posArgs = cmd.getArgs();
    if (posArgs.length < 2) {
      HelpFormatter fmt = new HelpFormatter();
      fmt.printHelp("java MergeImgSets IMG_SET_LIST OUT_FN", opts);
      System.exit(2);
    }
    String setsFn = posArgs[0];
    String outFn = posArgs[1];
    int replication = 1;
    if (cmd.hasOption("replication")) {
      replication = Integer.parseInt(cmd.getOptionValue("replication"));
    }

    List<List<String>> filesets = getFilesets(setsFn);
    int sizeZ = filesets.size();
    if (0 == sizeZ) {
      System.out.println("File set list is empty, nothing to do.");
      System.exit(0);
    }
    int sizeC = filesets.get(0).size();
    for (List<String> fs: filesets) {
      if (fs.size() != sizeC) {
        System.err.println("File sets must have equal size");
        System.exit(1);
      }
    }
    write(filesets, outFn, replication);
  }

}
