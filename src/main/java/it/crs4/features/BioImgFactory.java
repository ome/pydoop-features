/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2016 CRS4.
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

import java.util.List;
import java.util.Arrays;
import java.util.HashSet;
import java.nio.ByteBuffer;
import java.io.IOException;
import java.io.File;

import loci.formats.IFormatReader;
import loci.formats.ChannelSeparator;
import loci.formats.FormatException;

import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.file.DataFileWriter;


/**
 * Builds BioImgPlane Avro records from Bio-Formats image planes.
 */
public class BioImgFactory {

  private static final String DEFAULT_ORDER = "XYZCT";
  private static final int N_DIM = DEFAULT_ORDER.length();

  protected IFormatReader reader;
  protected String imgPath;
  protected String dimOrder;

  /** current series */
  protected int series = -1;

  /** indices of DEFAULT_ORDER chars as they appear in dimOrder */
  protected int[] dimIdx;

  /** a list containing the size of each dimension (in dimOrder order) */
  protected List<Integer> shape;

  /** Set the current series and populate dimOrder, dimIdx and shape */
  public void setSeries(int series) {
    if (this.series == series) {
      return;
    }
    reader.setSeries(series);
    this.series = series;
    dimOrder = reader.getDimensionOrder();
    if (dimOrder.length() != N_DIM) {
      throw new RuntimeException("the number of dimensions must be " + N_DIM);
    }
    dimIdx = new int[N_DIM];
    for (int i = 0; i < N_DIM; i++) {
      int idx = dimOrder.indexOf(DEFAULT_ORDER.charAt(i));
      if (idx < 0) {
        throw new RuntimeException(
          "dimension order is not a permutation of " + DEFAULT_ORDER);
      }
      dimIdx[i] = idx;
    }
    Integer[] s = new Integer[N_DIM];
    s[dimIdx[0]] = reader.getSizeX();
    s[dimIdx[1]] = reader.getSizeY();
    s[dimIdx[2]] = reader.getSizeZ();
    s[dimIdx[3]] = reader.getEffectiveSizeC();
    s[dimIdx[4]] = reader.getSizeT();
    shape = Arrays.asList(s);
  }

  /**
   * Constructs a BioImgFactory based on the given IFormatReader.
   *
   * NOTE: there is currently no protection against the reader's state
   * being changed by the caller. In particular, reader.setSeries
   * must not be called (call setSeries on the BioImgFactory instead).
   */
  public BioImgFactory(IFormatReader reader, String imgPath) {
    this.reader = new ChannelSeparator(reader);
    setSeries(this.reader.getSeries());
    this.imgPath = imgPath;
  }

  public int getSeries() {
    return series;
  }

  public int getSeriesCount() {
    return reader.getSeriesCount();
  }

  public BioImgPlane build(String name, int no)
      throws FormatException, IOException {
    return build(name, no, 0, 0, -1, -1, null, null);
  }

  public BioImgPlane build(String name, int no, int x, int y, int w, int h,
                           HashSet<Integer> zs, HashSet<Integer> ts)
      throws FormatException, IOException {
    if (w < 0) {
      w = shape.get(dimIdx[0]);
    }
    if (h < 0) {
      h = shape.get(dimIdx[1]);
    }
    int[] zct = reader.getZCTCoords(no);

    if (null != zs && !zs.contains(zct[0])) {
      return null;
    }
    if (null != ts && !ts.contains(zct[2])) {
      return null;
    }

    Integer[] offsets = new Integer[N_DIM];
    offsets[dimIdx[0]] = x;
    offsets[dimIdx[1]] = y;
    for (int i = 0; i < zct.length; i++) {
      offsets[dimIdx[i+2]] = zct[i];
    }
    Integer[] deltas = new Integer[N_DIM];
    deltas[dimIdx[0]] = w;
    deltas[dimIdx[1]] = h;
    for (int i = 0; i < zct.length; i++) {
      deltas[dimIdx[i+2]] = 1;
    }
    //--
    ArraySlice a = new ArraySlice();
    a.setDtype(ArrayTools.convertPixelType(reader.getPixelType()));
    a.setLittleEndian(reader.isLittleEndian());
    a.setShape(shape);
    a.setOffsets(Arrays.asList(offsets));
    a.setDeltas(Arrays.asList(deltas));
    a.setData(ByteBuffer.wrap(reader.openBytes(no, x, y, w, h)));
    return new BioImgPlane(name, imgPath, dimOrder, series, a);
  }

  public void writeSeries(String name, String fileName)
      throws FormatException, IOException {
    writeSeries(name, fileName, 0, 0, -1, -1, null, null);
  }

  public void writeSeries(String name, String fileName,
                          int x, int y, int w, int h,
                          HashSet<Integer> zs, HashSet<Integer> ts)
      throws FormatException, IOException {
    DataFileWriter<BioImgPlane> writer = new DataFileWriter<BioImgPlane>(
      new SpecificDatumWriter<BioImgPlane>(BioImgPlane.class)
    );
    boolean initialised = false;
    for (int i = 0; i < reader.getImageCount(); i++) {
      BioImgPlane plane = build(name, i, x, y, w, h, zs, ts);
      if (plane != null) {
        if (!initialised) {
          writer.create(plane.getSchema(), new File(fileName));
          initialised = true;
        }
        writer.append(plane);
      }
    }
    writer.close();
  }

}
