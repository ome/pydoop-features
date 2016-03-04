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
import java.io.PrintWriter;
import java.io.FileReader;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

import org.junit.Test;
import org.junit.ClassRule;
import org.junit.rules.TemporaryFolder;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class CSVReaderTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(
    CSVReaderTest.class);

  private static final String NAME = "temp";
  private static File target;

  @ClassRule
  public static TemporaryFolder wd = new TemporaryFolder();

  private void makeCSVFile(List<List<String>> rows, String delimiter)
      throws Exception {
    target = wd.newFile();
    PrintWriter out = new PrintWriter(target);
    for (List<String> r: rows) {
      StringBuilder builder = new StringBuilder();
      for (int i = 0; i < r.size() - 1; i++) {
        builder.append(r.get(i)).append(delimiter);
      }
      if (r.size() > 0) {
        builder.append(r.get(r.size() - 1));
      }
      out.print(builder.toString() + "\n");
    }
    out.close();
  }

  private void checkCSV(String delimiter) throws Exception {
    List<List<String>> data = new ArrayList<List<String>>();
    data.add(Arrays.asList("A", "B", "C"));
    data.add(Arrays.asList("D", "E", "F"));
    makeCSVFile(data, delimiter);
    String fname = target.getAbsolutePath();
    LOGGER.info("CSV file: {}", fname);
    FileReader in = new FileReader(fname);
    CSVReader reader = null;
    if ("," == delimiter) {
      reader = new CSVReader(in);  // check default
    } else {
      reader = new CSVReader(in, delimiter);
    }
    List<List<String>> read_data = new ArrayList<List<String>>();
    List<String> row;
    while (true) {
      row = reader.getRow();
      if (null == row) {
        break;
      }
      read_data.add(row);
    }
    reader.close();
    assertEquals(read_data.size(), data.size());
    for (int i = 0; i < read_data.size(); i++) {
      assertEquals(read_data.get(i).size(), data.get(i).size());
    }
  }

  @Test
  public void testDefault() throws Exception {
    checkCSV(",");
  }

  @Test
  public void testTab() throws Exception {
    checkCSV("\t");
  }

}
