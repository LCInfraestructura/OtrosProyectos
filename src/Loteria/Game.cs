using System.IO;
namespace Loteria;
public sealed class Card
{
 public int Id { get; set; }
 public int Number { get; set; }
 public string Name { get; set; } = "";
 public string Title { get; set; } = "";
 public string Slug { get; set; } = "";
 public Dictionary<string,string> Images { get; set; } = [];
 public Dictionary<string,string> Audio { get; set; } = [];
}
public sealed class Deck
{
 readonly List<Card> cards;
 int index;
 public int Count => index;
 public bool Finished => index == cards.Count;
 public Deck(IEnumerable<Card> source, Random? random = null) {
  cards = source.ToList();
  if(cards.Count != 54 || !cards.Select(c=>c.Id).Order().SequenceEqual(Enumerable.Range(1,54)))
   throw new InvalidDataException("El catálogo debe contener exactamente los IDs 1 a 54.");
  random ??= Random.Shared;
  for(int i=cards.Count-1;i>0;i--) { int j=random.Next(i+1); (cards[i],cards[j])=(cards[j],cards[i]); }
 }
 public Card? Take() => Finished ? null : cards[index++];
}
