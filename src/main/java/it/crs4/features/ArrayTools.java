package it.crs4.features;

import loci.formats.FormatTools;


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
      default:
        throw new IllegalArgumentException("Unknown pixel type: " + pixelType);
    }
  }

}
