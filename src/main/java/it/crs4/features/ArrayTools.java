package it.crs4.features;

import java.util.ArrayList;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

import loci.formats.FormatTools;
import loci.formats.IFormatReader;


public final class ArrayTools {

  /**
   * Convert a Bio-Formats pixel type to DataBlock's DType format.
   */
  public static DType convertPixelType(int pixelType) {
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

  /**
   * Get the shape (a list containing the size of each dimension) of
   * the multidimensional data object from a Bio-Formats image reader.
   */
  public static ArrayList<Integer> getShape(IFormatReader reader)
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

}
