/**
 * BEGIN_COPYRIGHT
 *
 * Copyright (C) 2016 Open Microscopy Environment:
 *   - University of Dundee
 *   - CRS4
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

import org.junit.Test;
import org.junit.ClassRule;
import org.junit.BeforeClass;
import org.junit.rules.TemporaryFolder;


public class ImageToAvroTest {

  private static String imgFn;

  @ClassRule
  public static TemporaryFolder wd = new TemporaryFolder();

  @BeforeClass
  public static void makeImgFile() throws Exception {
    imgFn = BioImgFactoryTest.makeImgFile(wd);
  }

  @Test
  public void testMain() throws Exception {
    File outDir = new File(wd.getRoot(), "out");
    outDir.mkdir();
    ImageToAvro.main(new String[] {imgFn, "-o", outDir.getAbsolutePath()});
    File[] files = outDir.listFiles();
    assertEquals(files.length, BioImgFactoryTest.SERIES_COUNT);
  }

}
