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
  private static final int SERIES_COUNT = 2;
  private static final String DIM_ORDER = "XYZCT";
  private static final int W = 512;
  private static final int H = 256;
  private static final int Z = 5;
  private static final int C = 1;
  private static final int T = 2;

  private static final int SIZE = W * H * C * FormatTools.getBytesPerPixel(
    PIXEL_TYPE);
  private static final int PLANES_COUNT = Z * T;

  private static byte[][][] data;
  private static File target;

  private static byte[] makeImg() {
    byte[] img = new byte[SIZE];
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
        ptString, W, H, Z, C, T, C);
    }
    IFormatWriter writer = new ImageWriter();
    writer.setMetadataRetrieve(meta);
    writer.setId(target.getAbsolutePath());
    data = new byte[SERIES_COUNT][PLANES_COUNT][SIZE];
    for (int s = 0; s < SERIES_COUNT; s++) {
      writer.setSeries(s);
      for (int p = 0; p < Z*T; p++) {
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
    assertEquals(a.getDtype(), DType.UINT16);  // FIXME: use lookup table
    assertEquals(a.getLittleEndian().booleanValue(), LITTLE_ENDIAN);
    List<Integer> shape = a.getShape();
    assertEquals(shape.size(), DIM_ORDER.length());
    assertEquals(shape.get(0).intValue(), W);
    assertEquals(shape.get(1).intValue(), H);
    assertEquals(shape.get(2).intValue(), Z);
    assertEquals(shape.get(3).intValue(), C);
    assertEquals(shape.get(4).intValue(), T);
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
