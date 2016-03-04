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


public final class PathTools {

  private PathTools() {}

  public static String basename(String path) {
    int i = path.lastIndexOf("/");
    return (i < 0) ? path : path.substring(i + 1);
  }

  public static String stripext(String path) {
    int i = path.lastIndexOf(".");
    return (i < 0) ? path : path.substring(0, i);
  }

}
