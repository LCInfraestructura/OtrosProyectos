using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Windows.Media;
using System.Windows.Threading;
using Loteria;

static class Diagnostics {
 public static int AuditShuffle() {
  var cards=JsonSerializer.Deserialize<List<Card>>(File.ReadAllText("assets/loteria/manifest.json"),new JsonSerializerOptions {PropertyNameCaseInsensitive=true})!;
  const int trials=54000; var positions=new int[54,54];
  for(int trial=0;trial<trials;trial++) {
   var deck=new Deck(cards); var seen=new HashSet<int>();
   for(int pos=0;pos<54;pos++) { var c=deck.Take()!; if(!seen.Add(c.Id)) throw new Exception("Duplicate card"); positions[c.Id-1,pos]++; }
   if(!deck.Finished || deck.Take()!=null) throw new Exception("Incomplete deck");
  }
  var first=Enumerable.Range(0,54).Select(i=>positions[i,0]).ToArray();
  var all=positions.Cast<int>().ToArray();
  var result=new {trials, expectedPerCardPerPosition=1000,firstPositionMin=first.Min(),firstPositionMax=first.Max(),allPositionsMin=all.Min(),allPositionsMax=all.Max(),duplicates=0,missing=0,firstPositionCounts=first};
  Directory.CreateDirectory("artifacts"); File.WriteAllText("artifacts/shuffle-audit.json",JsonSerializer.Serialize(result,new JsonSerializerOptions{WriteIndented=true})); Console.WriteLine(JsonSerializer.Serialize(result)); return 0;
 }
 public static int ProbeAudio(string[] paths) {
  var records=new List<object>(); bool failed=false;
  foreach(var path in paths) for(int repeat=0;repeat<3;repeat++) {
   var frame=new DispatcherFrame(); var media=new MediaPlayer {Volume=0,SpeedRatio=1}; var watch=new Stopwatch(); double? natural=null; string? error=null;
   var timeout=new DispatcherTimer {Interval=TimeSpan.FromSeconds(20)};
   timeout.Tick+=(_,_)=> { error="timeout"; frame.Continue=false; };
   media.MediaOpened+=(_,_)=> { if(media.NaturalDuration.HasTimeSpan) natural=media.NaturalDuration.TimeSpan.TotalSeconds; watch.Start(); media.Play(); };
   media.MediaEnded+=(_,_)=> { watch.Stop(); frame.Continue=false; };
   media.MediaFailed+=(_,e)=> {error=e.ErrorException.Message; frame.Continue=false;};
   media.Open(new Uri(Path.GetFullPath(path))); timeout.Start(); Dispatcher.PushFrame(frame); timeout.Stop(); media.Close();
   failed|=error!=null; records.Add(new {path,repeat,naturalSeconds=natural,elapsedSeconds=watch.Elapsed.TotalSeconds,error});
  }
  Directory.CreateDirectory("artifacts"); var json=JsonSerializer.Serialize(records,new JsonSerializerOptions{WriteIndented=true}); File.WriteAllText("artifacts/audio-timing.json",json); Console.WriteLine(json); return failed?1:0;
 }
}
