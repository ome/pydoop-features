package it.crs4.features;

import java.util.List;
import java.util.Arrays;
import java.nio.ByteBuffer;
import java.io.IOException;

import loci.formats.IFormatReader;
import loci.formats.FormatException;


public class BioImgFactory {

  private static final String DEFAULT_ORDER = "XYZCT";
  private static final int N_DIM = DEFAULT_ORDER.length();

  protected IFormatReader reader;
  protected String dimOrder;

  /** indices of DEFAULT_ORDER chars as they appear in dimOrder */
  protected int[] dimIdx;

  /** a list containing the size of each dimension (in dimOrder order) */
  protected List<Integer> shape;

  public BioImgFactory(IFormatReader reader) {
    this.reader = reader;
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
    s[dimIdx[3]] = reader.getSizeC();
    s[dimIdx[4]] = reader.getSizeT();
    shape = Arrays.asList(s);
  }

  public BioImgPlane build(String name, int no)
      throws FormatException, IOException {
    return build(name, no, 0, 0, reader.getSizeX(), reader.getSizeY());
  }

  public BioImgPlane build(String name, int no, int x, int y, int w, int h)
      throws FormatException, IOException {
    int[] zct = reader.getZCTCoords(no);
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
    a.setData(ByteBuffer.wrap(reader.openBytes(no)));
    return new BioImgPlane(name, dimOrder, a);
  }

}
