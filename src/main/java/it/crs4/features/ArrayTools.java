/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2017 CRS4.
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

import loci.formats.FormatTools;


public final class ArrayTools {

  private ArrayTools() {}

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
