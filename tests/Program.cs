using System.IO;
using System.Reflection;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Loteria;

static class Program {
 [STAThread] static int Main(string[] args) {
  if(args.Contains("--audio-probe")) return Diagnostics.ProbeAudio(args.Skip(1).ToArray());
  if(args.Contains("--shuffle-audit")) return Diagnostics.AuditShuffle();
  try {
   var cards=JsonSerializer.Deserialize<List<Card>>(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"assets/loteria/manifest.json")),new JsonSerializerOptions { PropertyNameCaseInsensitive=true })!;
   for(int seed=0;seed<100;seed++) {
    var d=new Deck(cards,new Random(seed)); var ids=new HashSet<int>();
    while(!d.Finished) Assert(ids.Add(d.Take()!.Id),"Repeated card");
    Assert(ids.Count==54 && d.Take()==null,"Deck completion");
   }
   try { _=new Deck(cards.Take(53)); throw new Exception("Missing ID accepted"); } catch(InvalidDataException) {}
   try { _=new Deck(cards.Take(53).Append(cards[0])); throw new Exception("Duplicate ID accepted"); } catch(InvalidDataException) {}
   var app=new App(); app.InitializeComponent();
   Directory.CreateDirectory("artifacts");
   File.WriteAllText("artifacts/test-settings.json",JsonSerializer.Serialize(new { ImageSet="pixel",AudioSet="radioteca",Delay=3,Muted=false,Volume=0.0,FlipEnabled=true }));
   var window=new MainWindow(Path.GetFullPath("artifacts/test-settings.json")) { ShowInTaskbar=false, Opacity=0 };
   window.Show(); Pump(150);
   T Find<T>(string name) where T:class => (T)window.FindName(name);
   void Click(string name)=>Find<Button>(name).RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
   string Phase()=> (string)typeof(MainWindow).GetField("phase",BindingFlags.Instance|BindingFlags.NonPublic)!.GetValue(window)!;
   int Count()=>Find<ItemsControl>("History").Items.Count;
   Assert(((ComboBoxItem)Find<ComboBox>("AudioSet").SelectedItem).Tag.ToString()=="loteriacard","Retired preference migrates to available voice");
   Assert(!Find<StackPanel>("SettingsPanel").IsVisible,"Settings hidden from game screen");
   Dispatcher.CurrentDispatcher.BeginInvoke(DispatcherPriority.ContextIdle,new Action(()=> {
    var dialog=window.OwnedWindows.Cast<Window>().Single();
    Find<TextBox>("DelayInput").Text="6";
    Find<ComboBox>("AudioSet").SelectedIndex=3;
    dialog.UpdateLayout(); SaveVisual(dialog,"artifacts/settings-preview.png");
    ((Button)dialog.FindName("SaveSettings")).RaiseEvent(new RoutedEventArgs(Button.ClickEvent));
   }));
   Click("SettingsButton");
   Assert(File.ReadAllText("artifacts/test-settings.json").Contains("generated-en"),"Generated voice persists by stable key");
   Assert(Find<TextBox>("DelayInput").Text=="6" && !Find<StackPanel>("SettingsPanel").IsVisible,"Save settings and hide dialog");
   Dispatcher.CurrentDispatcher.BeginInvoke(DispatcherPriority.ContextIdle,new Action(()=> {
    Find<TextBox>("DelayInput").Text="9"; window.OwnedWindows.Cast<Window>().Single().Close();
   }));
   Click("SettingsButton"); Assert(Find<TextBox>("DelayInput").Text=="6","Closing settings cancels edits");
   Find<ComboBox>("ImageSet").SelectedIndex=0;
   Assert(cards.All(c=>!c.Audio.ContainsKey("radioteca") && c.Audio.ContainsKey("generated-es") && c.Audio.ContainsKey("generated-en") && c.Audio.ContainsKey("generated-verses-es")),"All classic cards have the new voices and no retired set");
   Find<ComboBox>("AudioSet").SelectedIndex=1;
   Find<CheckBox>("Muted").IsChecked=true;
   Find<TextBox>("DelayInput").Text="0.4";
   Click("StartButton"); Assert(Count()==1,"First card immediate");
   Click("StartButton"); Pump(650); Assert(Count()==1,"Pause must freeze countdown");
   Click("StartButton"); Pump(100); Assert(Count()==1,"Resume must preserve remaining delay");
   Pump(450); Assert(Count()==2,"Advance after delay");
   Click("StartButton");
   // A custom display title affects both main card and history without renaming assets.
   var loaded=(List<Card>)typeof(MainWindow).GetField("cards",BindingFlags.Instance|BindingFlags.NonPublic)!.GetValue(window)!;
   foreach(var c in loaded) c.Title="Título de prueba";
   Click("NextButton"); Assert(Find<TextBlock>("CurrentTitle").Text=="Título de prueba","Display title");
   var item=Find<ItemsControl>("History").Items[0]; Assert(item.GetType().GetProperty("Caption")!.GetValue(item)!.ToString()!.Contains("Título de prueba"),"History title");
   // Restore titles for the visual fixture.
   foreach(var c in loaded) c.Title=c.Name;
   for(int i=0;i<9;i++) Click("NextButton");
   window.Opacity=1; window.UpdateLayout();
   var image=new RenderTargetBitmap((int)window.ActualWidth,(int)window.ActualHeight,96,96,PixelFormats.Pbgra32); image.Render(window);
   Directory.CreateDirectory("artifacts"); var encoder=new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(image)); using(var file=File.Create("artifacts/app-preview.png")) encoder.Save(file);
   window.Width=950; window.Height=650; window.UpdateLayout(); SaveVisual(window,"artifacts/app-compact-preview.png");
   while(Count()<54) Click("NextButton");
   Click("NextButton"); Assert(Phase()=="finished","End of deck");
   // Restart from the completed state, no confirmation dialog.
   typeof(MainWindow).GetMethod("NewGame",BindingFlags.Instance|BindingFlags.NonPublic)!.Invoke(window,[window,new RoutedEventArgs()]);
   Assert(Count()==0,"Reset clears history");
   Find<CheckBox>("Muted").IsChecked=false; Find<Slider>("Volume").Value=0; Find<TextBox>("DelayInput").Text="0.4";
   Find<ComboBox>("AudioSet").SelectedIndex=2; Find<CheckBox>("FlipEnabled").IsChecked=true;
   Click("StartButton");
   var limit=DateTime.UtcNow.AddSeconds(15);
   while(Phase()=="loading" && DateTime.UtcNow<limit) Pump(30);
   Assert(Phase()=="playing","WPF audio must open");
   Click("StartButton"); Pump(250); Assert(Count()==1,"Pause during audio"); Click("StartButton");
   bool sawFlip=false, sawVoice=false;
   while((Phase()=="playing" || Phase()=="loading") && DateTime.UtcNow<limit) {
    Assert(Count()==1,"No advance before effect and voice end");
    if(Phase()=="playing") { bool flip=(bool)typeof(MainWindow).GetField("playingFlip",BindingFlags.Instance|BindingFlags.NonPublic)!.GetValue(window)!; sawFlip|=flip; sawVoice|=!flip; }
    Pump(20);
   }
   Assert(sawFlip && sawVoice,"Must play flip then voice");
   Assert(Phase()=="waiting" && Count()==1,"Audio must finish before countdown");
   Pump(100); Assert(Count()==1,"Post-audio delay"); Pump(450); Assert(Count()==2,"Audio plus delay advances");
   window.Close(); Console.WriteLine("PASS: 100 shuffled decks, validation, pause/resume, display titles, history, reset, WPF audio plus delay, UI render."); return 0;
  } catch(Exception e) { Console.Error.WriteLine(e); return 1; }
 }
 static void Assert(bool value,string reason) { if(!value) throw new Exception(reason); }
 static void SaveVisual(Window window,string path) { Directory.CreateDirectory("artifacts"); var bitmap=new RenderTargetBitmap((int)window.ActualWidth,(int)window.ActualHeight,96,96,PixelFormats.Pbgra32); bitmap.Render(window); var encoder=new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); using var file=File.Create(path); encoder.Save(file); }
 static void Pump(int ms) { var frame=new DispatcherFrame(); var t=new DispatcherTimer { Interval=TimeSpan.FromMilliseconds(ms) }; t.Tick+=(_,_)=> { t.Stop(); frame.Continue=false; }; t.Start(); Dispatcher.PushFrame(frame); }
}
