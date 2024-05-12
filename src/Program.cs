using System;

using OSGeo.GDAL;

public class Program {
  public static async Task Main(string[] args) {
    if (args.Length < 3) {
      Console.WriteLine("Usage: NITF_Ranger.exe http://host.name/path/to/file.ntf '[minX, maxX, minY, maxY]' ./path/to/output.tiff");
      return;
    }
    string file_url = args[0];
    string bbox_str = args[1];
    string output_file = args[2];

    Console.WriteLine($"Reading metadata from {file_url}");

    try {
      Gdal.AllRegister();
    }
    catch (Exception ex) {
      Console.WriteLine(""+ex);
    }

    Dataset ds = Gdal.Open("/vsicurl/"+file_url, Access.GA_ReadOnly );
    Console.WriteLine("ds = "+ds);



  }
}
