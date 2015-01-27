package it.crs4.features;


public final class PathTools {

  public static String basename(String path) {
    int i = path.lastIndexOf("/");
    return (i < 0) ? path : path.substring(i + 1);
  }

  public static String stripext(String path) {
    int i = path.lastIndexOf(".");
    return (i < 0) ? path : path.substring(0, i);
  }

}
