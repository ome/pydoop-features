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
    //-- FIXME: add support for XY slicing --
    int offsetX = 0;
    int offsetY = 0;
    int deltaX = reader.getSizeX();
    int deltaY = reader.getSizeY();
    //---------------------------------------
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
      int nDim = dimOrder.length();
      int iX = dimOrder.indexOf('X');
      int iY = dimOrder.indexOf('Y');
      int iZ = dimOrder.indexOf('Z');
      int iC = dimOrder.indexOf('C');
      int iT = dimOrder.indexOf('T');
      Integer[] offsets = new Integer[nDim];
      offsets[iX] = offsetX;
      offsets[iY] = offsetY;
      offsets[iZ] = zct[0];
      offsets[iC] = zct[1];
      offsets[iT] = zct[2];
      Integer[] deltas = new Integer[nDim];
      deltas[iX] = deltaX;
      deltas[iY] = deltaY;
      deltas[iZ] = 1;
      deltas[iC] = 1;
      deltas[iT] = 1;
      //--
      ArraySlice a = new ArraySlice();
      a.setDtype(convertPT(reader.getPixelType()));
      a.setLittleEndian(reader.isLittleEndian());
      a.setShape(shape);
      a.setOffsets(Arrays.asList(offsets));
      a.setDeltas(Arrays.asList(deltas));
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
