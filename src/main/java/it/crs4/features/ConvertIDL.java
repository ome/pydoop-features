package it.crs4.features;

import java.io.File;
import java.util.List;
import java.util.ArrayList;

import org.apache.avro.tool.IdlToSchemataTool;


/**
 * Convert *.avdl to *.avsc
 * http://www.virtualroadside.com/blog/index.php/2014/06/08/automatically-generating-avro-schemata-avsc-files-using-maven/
 */
public class ConvertIDL {

  public static void main(String[] args) throws Exception {
    if (args.length < 2) {
      System.err.println("Usage: java ConvertIDL IN_DIR OUT_DIR");
      return;
    }
    File inDir = new File(args[0]);
    File outDir = new File(args[1]);

    IdlToSchemataTool tool = new IdlToSchemataTool();
    for (File inFile: inDir.listFiles()) {
      List<String> toolArgs = new ArrayList<String>();
      toolArgs.add(inFile.getAbsolutePath());
      toolArgs.add(outDir.getAbsolutePath());
      tool.run(System.in, System.out, System.err, toolArgs);
    }
  }
}
