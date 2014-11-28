package it.crs4.features;

import java.io.File;
import java.nio.ByteBuffer;

import loci.formats.ImageReader;
import loci.formats.FormatTools;

import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.file.DataFileWriter;


public class App {

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
      assert seriesCount == 1;
      assert !reader.isRGB();
      reader.setSeries(0);
      int pixelType = reader.getPixelType();  // FIXME: convert to avro enum
      int sizeX = reader.getSizeX();
      int sizeY = reader.getSizeY();
      DataFileWriter<BioImgPlane> writer = new DataFileWriter<BioImgPlane>(
        new SpecificDatumWriter<BioImgPlane>(BioImgPlane.class)
      );
      for (int i = 0; i < reader.getImageCount(); i++) {
        BioImgPlane plane = new BioImgPlane();
        plane.setName(bn);
        plane.setIndex(i);
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
    } catch (Exception e) {
      System.err.println("ERROR: " + e.getMessage());
      return;
    }
  }

}
