package it.crs4.features;

import java.io.File;

import loci.formats.ImageReader;

import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.file.DataFileWriter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class App {

  private static final Logger LOGGER = LoggerFactory.getLogger(App.class);

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
    reader.setSeries(0);
    BioImgFactory factory = new BioImgFactory(reader);
    DataFileWriter<BioImgPlane> writer = new DataFileWriter<BioImgPlane>(
      new SpecificDatumWriter<BioImgPlane>(BioImgPlane.class)
    );
    int nPlanes = reader.getImageCount();
    LOGGER.info("Reading from {}", fn);
    LOGGER.info("Writing to {}", outFn);
    for (int i = 0; i < nPlanes; i++) {
      // FIXME: add support for XY slicing
      BioImgPlane plane = factory.build(name, i);
      if (i == 0) {
        writer.create(plane.getSchema(), new File(outFn));
      }
      writer.append(plane);
    }
    writer.close();
    reader.close();
    LOGGER.info("All done");
  }

}
