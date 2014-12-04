package it.crs4.features;

import java.io.File;
import java.io.PrintWriter;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.ArrayList;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

import loci.formats.ImageReader;
import loci.formats.FormatTools;

import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.file.DataFileWriter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class App {

  private static final Logger LOGGER = LoggerFactory.getLogger(App.class);

  private static DType convertPT(int pixelType) {
    switch (pixelType) {
      case FormatTools.INT8:
        return DType.INT8;
      case FormatTools.UINT8:
        return DType.UINT8;
      case FormatTools.INT16:
        return DType.INT16;
      case FormatTools.UINT16:
        return DType.UINT16;
      case FormatTools.INT32:
        return DType.INT32;
      case FormatTools.UINT32:
        return DType.UINT32;
      case FormatTools.FLOAT:
        return DType.FLOAT32;
      case FormatTools.DOUBLE:
        return DType.FLOAT64;
    }
    throw new IllegalArgumentException("Unknown pixel type: " + pixelType);
  }

  private static String basename(String path) {
    int i = path.lastIndexOf("/");
    return (i < 0) ? path : path.substring(i + 1);
  }

  private static ArrayList<Integer> getShape(ImageReader reader)
    throws NoSuchMethodException,
           IllegalAccessException,
           InvocationTargetException {
    String dimOrder = reader.getDimensionOrder();
    ArrayList<Integer> shape = new ArrayList<Integer>();
    for (int i = 0; i < dimOrder.length(); i++) {
      String getterName = "getSize" + dimOrder.charAt(i);
      Method method = reader.getClass().getMethod(getterName);
      shape.add((Integer) method.invoke(reader));
    }
    return shape;
  }

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      System.err.println("Usage: java App IMG_FILE");
      return;
    }
    String fn = args[0];
    String bn = basename(fn);
    String outFn = bn + ".avro";
    int offsetX = 0;  // FIXME
    int offsetY = 0;  // FIXME

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
    ArrayList<Integer> shape = getShape(reader);
    DataFileWriter<BioImgPlane> writer = new DataFileWriter<BioImgPlane>(
      new SpecificDatumWriter<BioImgPlane>(BioImgPlane.class)
    );
    int nPlanes = reader.getImageCount();
    LOGGER.info("Reading from {}", fn);
    LOGGER.info("Writing to {}", outFn);
    for (int i = 0; i < nPlanes; i++) {
      int[] zct = reader.getZCTCoords(i);
      LOGGER.debug("Plane {}/{} {}", i + 1, nPlanes, Arrays.toString(zct));
      String dimOrder = reader.getDimensionOrder();
      Integer[] offsets = new Integer[dimOrder.length()];
      offsets[dimOrder.indexOf('X')] = offsetX;
      offsets[dimOrder.indexOf('Y')] = offsetY;
      offsets[dimOrder.indexOf('Z')] = zct[0];
      offsets[dimOrder.indexOf('C')] = zct[1];
      offsets[dimOrder.indexOf('T')] = zct[2];
      //--
      MultiArray a = new MultiArray();
      a.setDtype(convertPT(reader.getPixelType()));
      a.setLittleEndian(reader.isLittleEndian());
      a.setShape(shape);
      a.setOffsets(Arrays.asList(offsets));
      a.setData(ByteBuffer.wrap(reader.openBytes(i)));
      BioImgPlane plane = new BioImgPlane(bn, dimOrder, a);
      //--
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
