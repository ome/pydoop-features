package it.crs4.features;

import java.io.File;
import java.nio.ByteBuffer;
import java.util.Arrays;

import loci.formats.ImageReader;
import loci.formats.FormatTools;

import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.file.DataFileWriter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class App {

  private static final Logger LOGGER = LoggerFactory.getLogger(App.class);

  private static PixelTypes[] ptValues = PixelTypes.values();

  private static PixelTypes convertPT(int t) {
    return ptValues[t];
  }

  private static String basename(String path) {
    int i = path.lastIndexOf("/");
    return (i < 0) ? path : path.substring(i + 1);
  }

  public static void main(String[] args) {
    if (args.length == 0) {
      System.err.println("Usage: java App IMG_FILE");
      return;
    }
    String fn = args[0];
    String bn = basename(fn);
    String outFn = bn + ".avro";

    try {
      ImageReader reader = new ImageReader();
      reader.setId(fn);
      int seriesCount = reader.getSeriesCount();
      if (seriesCount != 1) {
        throw new RuntimeException("Multi-series img not supported");
      }
      if (reader.isRGB()) {
        throw new RuntimeException("RGB img not supported");
      }
      reader.setSeries(0);
      int pixelType = reader.getPixelType();
      int sizeX = reader.getSizeX();
      int sizeY = reader.getSizeY();
      DataFileWriter<BioImgPlane> writer = new DataFileWriter<BioImgPlane>(
        new SpecificDatumWriter<BioImgPlane>(BioImgPlane.class)
      );
      int nPlanes = reader.getImageCount();
      LOGGER.info("Reading from {}", fn);
      LOGGER.info("Writing to {}", outFn);
      for (int i = 0; i < nPlanes; i++) {
        int[] zct = reader.getZCTCoords(i);
        LOGGER.debug("Plane {}/{} {}", i + 1, nPlanes, Arrays.toString(zct));
        BioImgPlane plane = new BioImgPlane();
        plane.setName(bn);
        plane.setIndex(i);
        plane.setIndexZ(zct[0]);
        plane.setIndexC(zct[1]);
        plane.setIndexT(zct[2]);
        plane.setOffsetX(0);  // FIXME
        plane.setOffsetY(0);  // FIXME
        plane.setSizeX(sizeX);
        plane.setSizeY(sizeY);
        plane.setData(ByteBuffer.wrap(reader.openBytes(i)));
        plane.setPixelType(convertPT(pixelType));
        //--
        if (i == 0) {
          writer.create(plane.getSchema(), new File(outFn));
        }
        writer.append(plane);
      }
      writer.close();
      reader.close();
      LOGGER.info("All done");
    } catch (Exception e) {
      System.err.println("ERROR: " + e.getMessage());
      return;
    }
  }

}
