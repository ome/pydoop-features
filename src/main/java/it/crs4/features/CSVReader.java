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

import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

import java.io.Reader;
import java.io.BufferedReader;
import java.io.IOException;


public class CSVReader {

  private BufferedReader reader;
  private String delimiter;

  public CSVReader(Reader reader, String delimiter) {
    this.reader = new BufferedReader(reader);
    this.delimiter = delimiter;
  }

  public CSVReader(Reader reader) {
    this(reader, ",");
  }

  public List<String> getRow() throws IOException {
    String line = reader.readLine();
    if (null == line) {
      return null;
    }
    StringTokenizer tokenizer = new StringTokenizer(line.trim(), delimiter);
    List<String> row = new ArrayList<String>();
    while (tokenizer.hasMoreTokens()) {
      row.add(tokenizer.nextToken());
    }
    return row;
  }

  public void close() throws IOException {
    reader.close();
  }

}
