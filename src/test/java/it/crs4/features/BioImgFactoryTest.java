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

import static org.junit.Assert.assertEquals;

import java.io.File;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.Collections;
import java.util.Arrays;
import java.nio.ByteBuffer;

import org.junit.Test;
import org.junit.ClassRule;
import org.junit.BeforeClass;
import org.junit.rules.TemporaryFolder;

import loci.formats.FormatTools;
import loci.formats.MetadataTools;
import loci.formats.IFormatReader;
import loci.formats.IFormatWriter;
import loci.formats.ImageWriter;
import loci.formats.ImageReader;
import loci.formats.ChannelSeparator;
import loci.formats.meta.IMetadata;
import loci.common.services.ServiceFactory;
import loci.formats.services.OMEXMLService;

import org.apache.avro.specific.SpecificDatumReader;
import org.apache.avro.file.DataFileReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class BioImgFactoryTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(
    BioImgFactoryTest.class);

  // independent
  private static final String NAME = "pydoop_features_test";
  private static final boolean LITTLE_ENDIAN = true;
  private static final int PIXEL_TYPE = FormatTools.UINT16;
  private static final DType EXPECTED_DTYPE = DType.UINT16;
  private static final String DIM_ORDER = "XYCZT";
  private static final int SERIES_COUNT = 2;
  // use different size{X,Y,Z} for the two series
  private static final int[] SIZE_X = {512, 256};
  private static final int[] SIZE_Y = {256, 128};
  private static final int[] SIZE_Z = {5, 4};
  private static final int EFF_SIZE_C = 1;
  private static final int SIZE_T = 2;
  private static final int SPP = 3;  // Samples per pixel (e.g., 3 for RGB)

  // dependent
  private static final int[] PLANE_SIZE = {
    SIZE_X[0] * SIZE_Y[0] * FormatTools.getBytesPerPixel(PIXEL_TYPE),
    SIZE_X[1] * SIZE_Y[1] * FormatTools.getBytesPerPixel(PIXEL_TYPE)
  };
  private static final int[] RGB_PLANE_SIZE = {
    PLANE_SIZE[0] * SPP,
    PLANE_SIZE[1] * SPP
  };
  private static final int[] RGB_PLANES_COUNT = {
    EFF_SIZE_C * SIZE_Z[0] * SIZE_T,
    EFF_SIZE_C * SIZE_Z[1] * SIZE_T
  };
  private static final int[] PLANES_COUNT = {
    SPP * RGB_PLANES_COUNT[0],
    SPP * RGB_PLANES_COUNT[1]
  };
  private static final int SIZE_C = SPP * EFF_SIZE_C;

  private static byte[][][] data;
  private static File target;

  // store zct -> index mapping for all series
  private static List<Map<List<Integer>, Integer>> zct2i =
    new ArrayList<Map<List<Integer>, Integer>>();

  private static void putIndex(int s, int z, int c, int t, int i) {
    zct2i.get(s).put(Collections.unmodifiableList(Arrays.asList(z, c, t)), i);
  }

  private static int getIndex(int s, int z, int c, int t) {
    return zct2i.get(s).get(
        Collections.unmodifiableList(Arrays.asList(z, c, t))
    );
  }

  private static int getIndex(int s, List<Integer> offsets) {
    return getIndex(s, offsets.get(3), offsets.get(2), offsets.get(4));
  }

  private static byte[] makeImg(int size) {
    byte[] img = new byte[size];
    for (int i = 0; i < img.length; i++) {
      img[i] = (byte) (256 * Math.random());
    }
    return img;
  }

  @ClassRule
  public static TemporaryFolder wd = new TemporaryFolder();

  @BeforeClass
  public static void makeImgFile() throws Exception {
    LOGGER.info("wd: {}", wd.getRoot());
    target = wd.newFile(String.format("%s.ome.tiff", NAME));
    String imgFn = target.getAbsolutePath();
    String ptString = FormatTools.getPixelTypeString(PIXEL_TYPE);
    ServiceFactory factory = new ServiceFactory();
    OMEXMLService service = factory.getInstance(OMEXMLService.class);
    IMetadata meta = service.createOMEXMLMetadata();
    for (int s = 0; s < SERIES_COUNT; s++) {
      MetadataTools.populateMetadata(meta, s, null, LITTLE_ENDIAN, DIM_ORDER,
        ptString, SIZE_X[s], SIZE_Y[s], SIZE_Z[s], SIZE_C, SIZE_T, SPP);
    }
    IFormatWriter writer = new ImageWriter();
    writer.setMetadataRetrieve(meta);
    writer.setId(imgFn);
    writer.setInterleaved(false);
    data = new byte[SERIES_COUNT][][];
    for (int s = 0; s < SERIES_COUNT; s++) {
      data[s] = new byte[RGB_PLANES_COUNT[s]][];
      writer.setSeries(s);
      for (int p = 0; p < RGB_PLANES_COUNT[s]; p++) {
        byte[] img = makeImg(RGB_PLANE_SIZE[s]);
        writer.saveBytes(p, img);
        data[s][p] = img;
      }
    }
    writer.close();
    //-- Store zct -> index mapping --
    IFormatReader reader = new ImageReader();
    reader.setId(imgFn);
    reader = new ChannelSeparator(reader);
    for (int s = 0; s < SERIES_COUNT; s++) {
      reader.setSeries(s);
      zct2i.add(new HashMap<List<Integer>, Integer>());
      for (int z = 0; z < reader.getSizeZ(); z++) {
        for (int c = 0; c < reader.getSizeC(); c++) {
          for (int t = 0; t < reader.getSizeT(); t++) {
            putIndex(s, z, c, t, reader.getIndex(z, c, t));
          }
        }
      }
    }
  }

  private void checkPlane(BioImgPlane p, int seriesIdx) {
    ArraySlice a = p.getPixelData();
    List<Integer> offsets = a.getOffsets();
    for (int i = 0; i < 2; i ++) {
      assertEquals(offsets.get(i).intValue(), 0);
    }
    // Other offsets checked implicitly: if wrong, fetched plane will be wrong
    int planeIdx = getIndex(seriesIdx, offsets);
    int rgbPlaneIdx = planeIdx / SPP;
    int sampleIdx = planeIdx % SPP;
    byte[] expBytes = Arrays.copyOfRange(
        data[seriesIdx][rgbPlaneIdx],
        PLANE_SIZE[seriesIdx] * sampleIdx,
        PLANE_SIZE[seriesIdx] * (sampleIdx + 1)
    );
    assertEquals(p.getDimensionOrder().toString(), DIM_ORDER);
    assertEquals(p.getSeries().intValue(), seriesIdx);
    assertEquals(a.getDtype(), EXPECTED_DTYPE);
    assertEquals(a.getLittleEndian().booleanValue(), LITTLE_ENDIAN);
    //--
    List<Integer> shape = a.getShape();
    assertEquals(shape.size(), DIM_ORDER.length());
    assertEquals(shape.get(0).intValue(), SIZE_X[seriesIdx]);
    assertEquals(shape.get(1).intValue(), SIZE_Y[seriesIdx]);
    assertEquals(shape.get(2).intValue(), SIZE_C);
    assertEquals(shape.get(3).intValue(), SIZE_Z[seriesIdx]);
    assertEquals(shape.get(4).intValue(), SIZE_T);
    //--
    List<Integer> deltas = a.getDeltas();
    assertEquals(deltas.get(0).intValue(), SIZE_X[seriesIdx]);
    assertEquals(deltas.get(1).intValue(), SIZE_Y[seriesIdx]);
    for (int i = 2; i < 5; i ++) {
      assertEquals(deltas.get(i).intValue(), 1);
    }
    //--
    ByteBuffer buffer = a.getData();
    buffer.clear();
    for (byte b: expBytes) {
      assertEquals(buffer.get(), b);
    }
  }

  @Test
  public void testWriteSeries() throws Exception {
    String imgFn = target.getAbsolutePath();
    LOGGER.info("Image file: {}", imgFn);
    IFormatReader iReader = new ImageReader();
    iReader.setId(imgFn);
    BioImgFactory factory = new BioImgFactory(iReader, imgFn);
    assertEquals(factory.getSeriesCount(), SERIES_COUNT);
    for (int s = 0; s < SERIES_COUNT; s++) {
      LOGGER.info("Series: {}", s);
      String name = String.format("%s_%d", NAME, s);
      File avroF = wd.newFile(String.format("%s.avro", name));
      String avroFn = avroF.getAbsolutePath();
      LOGGER.info("Avro file: {}", avroFn);
      factory.setSeries(s);
      assertEquals(factory.getSeries(), s);
      factory.writeSeries(name, avroFn);
      //--
      DataFileReader<BioImgPlane> aReader = new DataFileReader<BioImgPlane>(
        avroF, new SpecificDatumReader<BioImgPlane>(BioImgPlane.class)
      );
      int planeIdx = 0;
      BioImgPlane p = null;
      while (aReader.hasNext()) {
        p = aReader.next(p);
        assertEquals(getIndex(s, p.getPixelData().getOffsets()), planeIdx);
        checkPlane(p, s);
        planeIdx++;
      }
      assertEquals(planeIdx, PLANES_COUNT[s]);
    }
    iReader.close();
  }

}
