/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2014-2015 CRS4.
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
import java.nio.ByteBuffer;

import org.junit.Test;
import org.junit.ClassRule;
import org.junit.BeforeClass;
import org.junit.rules.TemporaryFolder;

import loci.formats.FormatTools;
import loci.formats.MetadataTools;
import loci.formats.IFormatWriter;
import loci.formats.ImageWriter;
import loci.formats.ImageReader;
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

  private static final String NAME = "pydoop_features_test";
  private static final boolean LITTLE_ENDIAN = true;
  private static final int PIXEL_TYPE = FormatTools.UINT16;
  private static final DType EXPECTED_DTYPE = DType.UINT16;
  private static final int SERIES_COUNT = 2;
  private static final String DIM_ORDER = "XYZCT";
  private static final int SIZE_X = 512;
  private static final int SIZE_Y = 256;
  private static final int SIZE_Z = 5;
  private static final int SIZE_C = 1;
  private static final int SIZE_T = 2;
  private static final int SPP = 1;  // Samples per pixel (e.g., 3 for RGB)

  private static final int PLANE_SIZE =
    SIZE_X * SIZE_Y * SPP * FormatTools.getBytesPerPixel(PIXEL_TYPE);
  private static final int PLANES_COUNT = SIZE_Z * SIZE_T;

  private static byte[][][] data;
  private static File target;

  private static byte[] makeImg() {
    byte[] img = new byte[PLANE_SIZE];
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
    String ptString = FormatTools.getPixelTypeString(PIXEL_TYPE);
    ServiceFactory factory = new ServiceFactory();
    OMEXMLService service = factory.getInstance(OMEXMLService.class);
    IMetadata meta = service.createOMEXMLMetadata();
    for (int s = 0; s < SERIES_COUNT; s++) {
      MetadataTools.populateMetadata(meta, s, null, LITTLE_ENDIAN, DIM_ORDER,
        ptString, SIZE_X, SIZE_Y, SIZE_Z, SIZE_C, SIZE_T, SPP);
    }
    IFormatWriter writer = new ImageWriter();
    writer.setMetadataRetrieve(meta);
    writer.setId(target.getAbsolutePath());
    data = new byte[SERIES_COUNT][PLANES_COUNT][PLANE_SIZE];
    for (int s = 0; s < SERIES_COUNT; s++) {
      writer.setSeries(s);
      for (int p = 0; p < PLANES_COUNT; p++) {
        byte[] img = makeImg();
        writer.saveBytes(p, img);
        data[s][p] = img;
      }
    }
    writer.close();
  }

  private void checkPlane(BioImgPlane p, int seriesIdx, int planeIdx) {
    assertEquals(p.getDimensionOrder().toString(), DIM_ORDER);
    ArraySlice a = p.getPixelData();
    assertEquals(a.getDtype(), EXPECTED_DTYPE);
    assertEquals(a.getLittleEndian().booleanValue(), LITTLE_ENDIAN);
    List<Integer> shape = a.getShape();
    assertEquals(shape.size(), DIM_ORDER.length());
    assertEquals(shape.get(0).intValue(), SIZE_X);
    assertEquals(shape.get(1).intValue(), SIZE_Y);
    assertEquals(shape.get(2).intValue(), SIZE_Z);
    assertEquals(shape.get(3).intValue(), SIZE_C);
    assertEquals(shape.get(4).intValue(), SIZE_T);
    ByteBuffer buffer = a.getData();
    buffer.clear();
    for (byte b: data[seriesIdx][planeIdx]) {
      assertEquals(buffer.get(), b);
    }
  }

  @Test
  public void testWriteSeries() throws Exception {
    String imgFn = target.getAbsolutePath();
    LOGGER.info("Image file: {}", imgFn);
    ImageReader iReader = new ImageReader();
    iReader.setId(imgFn);
    BioImgFactory factory = new BioImgFactory(iReader);
    for (int s = 0; s < SERIES_COUNT; s++) {
      LOGGER.info("Series: {}", s);
      String name = String.format("%s_%d", NAME, s);
      File avroF = wd.newFile(String.format("%s.avro", name));
      String avroFn = avroF.getAbsolutePath();
      LOGGER.info("Avro file: {}", avroFn);
      factory.writeSeries(s, name, avroFn);
      //--
      DataFileReader<BioImgPlane> aReader = new DataFileReader<BioImgPlane>(
        avroF, new SpecificDatumReader<BioImgPlane>(BioImgPlane.class)
      );
      int planeIdx = 0;
      BioImgPlane p = null;
      while (aReader.hasNext()) {
        p = aReader.next(p);
        checkPlane(p, s, planeIdx);
        planeIdx++;
      }
      assertEquals(planeIdx, PLANES_COUNT);
    }
    iReader.close();
  }

}
