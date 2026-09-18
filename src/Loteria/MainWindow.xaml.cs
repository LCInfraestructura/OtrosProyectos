using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace Loteria;
public partial class MainWindow : Window
{
 readonly string root = Path.Combine(AppContext.BaseDirectory,"assets","loteria");
 readonly string prefs;
 readonly DispatcherTimer timer = new() { Interval = TimeSpan.FromMilliseconds(50) };
 readonly Stopwatch clock = Stopwatch.StartNew();
 readonly Dictionary<int,BitmapSource> images = [];
 readonly ObservableCollection<object> history = [];
 List<Card> cards = [];
 Deck? deck;
 MediaPlayer? player;
 string imageSet="pixel", audioSet="loteriacard", phase="idle", flipPath="";
 bool paused, silent, flipEnabled, playingFlip;
 double delay=3, deadline, remaining, loadDeadline;
 int generation;
 WindowState previousState;
 public MainWindow() : this(null) { }
 public MainWindow(string? preferencesPath) {
  prefs=preferencesPath ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"LoteriaOficina","settings.json");
  InitializeComponent(); History.ItemsSource=history;
  BrandLogo.Source=new BitmapImage(new Uri(Path.Combine(AppContext.BaseDirectory,"assets","branding","lc-logo.png")));
  timer.Tick += Tick; timer.Start();
  Volume.ValueChanged += (_,_)=> { if(player!=null) player.Volume=Volume.Value; };
  Loaded += (_,_)=>LoadCatalog();
  Closed += (_,_)=> { timer.Stop(); player?.Close(); };
 }
 void LoadCatalog() {
  try {
   cards=JsonSerializer.Deserialize<List<Card>>(File.ReadAllText(Path.Combine(root,"manifest.json")),new JsonSerializerOptions { PropertyNameCaseInsensitive=true }) ?? [];
   _=new Deck(cards);
   flipPath=JsonSerializer.Deserialize<Dictionary<string,string>>(File.ReadAllText(Path.Combine(root,"effects.json")))!["flipcard"];
   if(cards.Any(c=>string.IsNullOrWhiteSpace(c.Title) || c.Number!=c.Id)) throw new InvalidDataException("Cada carta requiere title y number igual a id.");
   if(File.Exists(prefs)) {
    try { var p=JsonSerializer.Deserialize<Preferences>(File.ReadAllText(prefs)); if(p!=null) {
     ImageSet.SelectedIndex=p.ImageSet=="traditional"?1:0;
     AudioSet.SelectedItem=AudioSet.Items.Cast<ComboBoxItem>().FirstOrDefault(item=>item.Tag.ToString()==p.AudioSet)
       ?? AudioSet.Items.Cast<ComboBoxItem>().Single(item=>item.Tag.ToString()=="loteriacard");
     FlipEnabled.IsChecked=p.FlipEnabled;
     DelayInput.Text=p.Delay.ToString(CultureInfo.CurrentCulture); Muted.IsChecked=p.Muted; Volume.Value=Math.Clamp(p.Volume,0,1);
    }} catch { /* Invalid preferences never prevent opening a valid catalog. */ }
   }
   Status.Text="Todo listo para la primera carta.";
  } catch(Exception ex) { Status.Text=ex.Message; StartButton.IsEnabled=NextButton.IsEnabled=false; }
 }
 string Asset(string relative) {
  var path=Path.GetFullPath(Path.Combine(root,relative));
  if(!path.StartsWith(Path.GetFullPath(root)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Ruta fuera del catálogo.");
  return path;
 }
 bool Prepare() {
  if(deck!=null) return true;
  if(!double.TryParse(DelayInput.Text,NumberStyles.Float,CultureInfo.CurrentCulture,out delay) || !double.IsFinite(delay) || delay<0.1 || delay>600) {
   Status.Text="Escribe una espera entre 0.1 y 600 segundos."; return false;
  }
  imageSet=((ComboBoxItem)ImageSet.SelectedItem).Tag.ToString()!;
  audioSet=((ComboBoxItem)AudioSet.SelectedItem).Tag.ToString()!; silent=Muted.IsChecked==true;
  flipEnabled=FlipEnabled.IsChecked==true;
  try {
   images.Clear();
   foreach(var card in cards) {
    var imagePath=Asset(card.Images[imageSet]);
    if(!File.Exists(imagePath)) throw new FileNotFoundException($"Carta {card.Id} · {card.Title}: falta {card.Images[imageSet]}");
    var bitmap=new BitmapImage(); bitmap.BeginInit(); bitmap.CacheOption=BitmapCacheOption.OnLoad; bitmap.UriSource=new Uri(imagePath); bitmap.EndInit(); bitmap.Freeze(); images[card.Id]=bitmap;
    if(!silent) {
     var audioPath=Asset(card.Audio[audioSet]);
     if(!File.Exists(audioPath)) throw new FileNotFoundException($"Carta {card.Id} · {card.Title}: falta el audio {audioSet}. Selecciona otro conjunto o Sin audio.");
     // Warm the OS file cache for the selected set only. WPF opens the local file for playback.
     using var stream=File.OpenRead(audioPath); stream.CopyTo(Stream.Null);
    }
   }
   if(!silent && flipEnabled && !File.Exists(Asset(flipPath))) throw new FileNotFoundException("Falta el sonido de giro. Desactívalo para jugar.");
   deck=new Deck(cards); SettingsPanel.IsEnabled=false;
   try { Directory.CreateDirectory(Path.GetDirectoryName(prefs)!); File.WriteAllText(prefs,JsonSerializer.Serialize(new Preferences(imageSet,audioSet,delay,silent,Volume.Value,flipEnabled))); } catch { /* Session can run without persistence. */ }
   return true;
  } catch(Exception ex) { Status.Text=ex.Message; return false; }
 }
 void StartPause(object sender,RoutedEventArgs e) {
  if(!Prepare()) return;
  if(phase=="idle") { ShowNext(); return; }
  if(phase=="finished") return;
  paused=!paused;
  if(paused) { if(phase=="waiting") remaining=Math.Max(0,deadline-clock.Elapsed.TotalSeconds); player?.Pause(); StartButton.Content="Continuar"; Status.Text="Partida pausada"; }
  else { if(phase=="waiting") deadline=clock.Elapsed.TotalSeconds+remaining; if(phase=="playing") player?.Play(); StartButton.Content="Pausar"; }
 }
 void Next(object sender,RoutedEventArgs e) { if(Prepare()) ShowNext(); }
 void ShowNext() {
  generation++; player?.Close(); player=null;
  var card=deck?.Take();
  if(card==null) { Finish(); return; }
  CurrentImage.Source=images[card.Id]; CurrentTitle.Text=card.Title;
  EmptyStage.Visibility=EmptyHistory.Visibility=CardHint.Visibility=Visibility.Collapsed;
  HistoryCount.Text=$"{deck!.Count} / 54";
  var scaling=imageSet=="pixel"?BitmapScalingMode.NearestNeighbor:BitmapScalingMode.HighQuality;
  RenderOptions.SetBitmapScalingMode(CurrentImage,scaling);
  Counter.Text=$"Carta {card.Number:00} · {deck!.Count} de 54";
  history.Insert(0,new { Image=images[card.Id], Caption=$"{card.Number:00} · {card.Title}", Scaling=scaling }); HistoryScroll.ScrollToTop();
  StartButton.IsEnabled=true; StartButton.Content=paused?"Continuar":"Pausar";
  if(silent) { BeginWait(); return; }
  if(flipEnabled) PlayClip(card,flipPath,true,()=>PlayClip(card,card.Audio[audioSet],false,BeginWait));
  else PlayClip(card,card.Audio[audioSet],false,BeginWait);
 }
 void PlayClip(Card card,string relative,bool isFlip,Action onEnded) {
  generation++; player?.Close(); playingFlip=isFlip;
  int version=generation; player=new MediaPlayer { Volume=Volume.Value }; var current=player;
  phase="loading"; loadDeadline=clock.Elapsed.TotalSeconds+15; Status.Text="Preparando audio…";
  current.MediaOpened += (_,_)=> { if(version!=generation) return; phase="playing"; if(!paused) current.Play(); };
  current.MediaEnded += (_,_)=> { if(version==generation) onEnded(); };
  current.MediaFailed += (_,e)=> { if(version==generation) AudioError(card,e.ErrorException.Message); };
  try { current.Open(new Uri(Asset(relative))); } catch(Exception ex) { AudioError(card,ex.Message); }
 }
 void AudioError(Card card,string message) {
  generation++; player?.Close(); player=null; paused=true; phase="error";
  StartButton.Content="Continuar"; Status.Text=$"No se pudo reproducir {card.Id} · {card.Title}. Pulsa Siguiente o Nueva partida. {message}";
  StartButton.IsEnabled=false;
 }
 void BeginWait() { phase="waiting"; remaining=delay; deadline=clock.Elapsed.TotalSeconds+delay; }
 void Tick(object? sender,EventArgs e) {
  if(phase=="loading" && clock.Elapsed.TotalSeconds>loadDeadline) { AudioError(cards.First(c=>c.Id==deckCardId()),"Tiempo de apertura agotado."); return; }
  if(paused) return;
  if(phase=="playing") Status.Text=playingFlip?"Girando la carta…":"Cantando la carta…";
  if(phase=="waiting") {
   var left=deadline-clock.Elapsed.TotalSeconds;
   Status.Text=$"Siguiente en {Math.Max(0,left):0.0} s";
   if(left<=0) { if(deck!.Finished) Finish(); else ShowNext(); }
  }
 }
 int deckCardId() => cards.First(c=>images.TryGetValue(c.Id,out var b) && ReferenceEquals(b,CurrentImage.Source)).Id;
 void Finish() { phase="finished"; paused=false; player?.Close(); Status.Text="¡Baraja completa! Las 54 cartas han salido."; StartButton.IsEnabled=NextButton.IsEnabled=false; }
 void NewGame(object sender,RoutedEventArgs e) {
  if(deck!=null && phase!="finished" && MessageBox.Show(this,"¿Terminar la partida actual y limpiar el historial?","Nueva partida",MessageBoxButton.YesNo,MessageBoxImage.Question)!=MessageBoxResult.Yes) return;
  generation++; player?.Close(); player=null; deck=null; phase="idle"; paused=false; history.Clear(); images.Clear();
  CurrentImage.Source=null; CurrentTitle.Text="Que comience la suerte."; Counter.Text="54 cartas";
  EmptyStage.Visibility=EmptyHistory.Visibility=CardHint.Visibility=Visibility.Visible; HistoryCount.Text="0 / 54";
  StartButton.Content="Iniciar"; StartButton.IsEnabled=NextButton.IsEnabled=cards.Count==54; SettingsPanel.IsEnabled=true; Status.Text="Lista para una nueva mezcla.";
 }
 void OpenSettings(object sender,RoutedEventArgs e) {
  if(deck!=null && !paused && phase!="finished" && phase!="error") StartPause(sender,e);
  var oldDelay=DelayInput.Text; var oldImage=ImageSet.SelectedIndex; var oldAudio=AudioSet.SelectedIndex;
  var oldMute=Muted.IsChecked; var oldFlip=FlipEnabled.IsChecked; var oldVolume=Volume.Value;
  bool saved=false;
  var dialog=new Window { Owner=this, Title="Configuración", Width=490, Height=740, MinWidth=440, MinHeight=600,
   WindowStartupLocation=WindowStartupLocation.CenterOwner, ResizeMode=ResizeMode.CanResize,
   Background=Background, Foreground=Foreground, FontFamily=FontFamily, ShowInTaskbar=false };
  var shell=new DockPanel();
  var heading=new StackPanel { Margin=new Thickness(28,24,28,12) };
  heading.Children.Add(new TextBlock { Text="A tu manera", FontFamily=new FontFamily("Georgia"), FontSize=30 });
  var note=new TextBlock { Text=deck==null?"Prepara la próxima ronda.":"La configuración se puede cambiar al iniciar una nueva partida.", TextWrapping=TextWrapping.Wrap, Margin=new Thickness(0,8,0,0), Foreground=new SolidColorBrush(Color.FromRgb(115,124,113)) };
  heading.Children.Add(note); DockPanel.SetDock(heading,Dock.Top); shell.Children.Add(heading);
  var footer=new StackPanel { Orientation=Orientation.Horizontal, HorizontalAlignment=HorizontalAlignment.Right, Margin=new Thickness(28,12,28,24) };
  var cancel=new Button { Content="Cancelar", Margin=new Thickness(0,0,10,0) }; cancel.Click+=(_,_)=>dialog.Close();
  var save=new Button { Name="SaveSettings", Content=deck==null?"Guardar y cerrar":"Cerrar", Background=new SolidColorBrush(Color.FromRgb(181,83,57)), Foreground=Brushes.White };
  NameScope.SetNameScope(dialog,new NameScope()); dialog.RegisterName("SaveSettings",save);
  save.Click+=(_,_)=> {
   if(deck==null) {
    if(!double.TryParse(DelayInput.Text,NumberStyles.Float,CultureInfo.CurrentCulture,out var value) || !double.IsFinite(value) || value<0.1 || value>600) { note.Text="Escribe una espera entre 0.1 y 600 segundos."; DelayInput.Focus(); return; }
    try {
     var settings=new Preferences(((ComboBoxItem)ImageSet.SelectedItem).Tag.ToString()!,((ComboBoxItem)AudioSet.SelectedItem).Tag.ToString()!,value,Muted.IsChecked==true,Volume.Value,FlipEnabled.IsChecked==true);
     Directory.CreateDirectory(Path.GetDirectoryName(prefs)!); File.WriteAllText(prefs,JsonSerializer.Serialize(settings));
    } catch(Exception ex) { note.Text=$"No se pudo guardar: {ex.Message}"; return; }
   }
   saved=true; dialog.Close();
  };
  if(deck==null) footer.Children.Add(cancel); footer.Children.Add(save); DockPanel.SetDock(footer,Dock.Bottom); shell.Children.Add(footer);
  SettingsHost.Child=null;
  var scroll=new ScrollViewer { Content=SettingsPanel, VerticalScrollBarVisibility=ScrollBarVisibility.Auto };
  shell.Children.Add(scroll); dialog.Content=shell;
  try { dialog.ShowDialog(); }
  finally {
   scroll.Content=null; SettingsHost.Child=SettingsPanel;
   if(!saved) { DelayInput.Text=oldDelay; ImageSet.SelectedIndex=oldImage; AudioSet.SelectedIndex=oldAudio; Muted.IsChecked=oldMute; FlipEnabled.IsChecked=oldFlip; Volume.Value=oldVolume; }
  }
 }
 void FullScreen(object sender,RoutedEventArgs e) {
  if(WindowStyle==WindowStyle.None) { WindowStyle=WindowStyle.SingleBorderWindow; WindowState=previousState; }
  else { previousState=WindowState; WindowState=WindowState.Normal; WindowStyle=WindowStyle.None; WindowState=WindowState.Maximized; }
 }
 void OnKeyDown(object sender,KeyEventArgs e) { if(e.Key==Key.F11 || (e.Key==Key.Escape && WindowStyle==WindowStyle.None)) { FullScreen(sender,e); e.Handled=true; } }
 record Preferences(string ImageSet,string AudioSet,double Delay,bool Muted,double Volume,bool FlipEnabled=true);
}
