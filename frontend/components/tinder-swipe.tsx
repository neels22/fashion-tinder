import { View } from 'react-native';
import { TinderCard } from './tinder-card';
import { useState } from 'react';

const cardsData = [
  { id: 1, name: 'John Doe', image: 'https://picsum.photos/200/300' },
  { id: 2, name: 'Jane Doe', image: 'https://picsum.photos/200/300' },
  { id: 3, name: 'John Smith', image: 'https://picsum.photos/200/300' },
  { id: 4, name: 'John Doe', image: 'https://picsum.photos/200/300' },
  { id: 5, name: 'Jane Doe', image: 'https://picsum.photos/200/300' },
  { id: 6, name: 'John Smith', image: 'https://picsum.photos/200/300' },
  { id: 7, name: 'John Doe', image: 'https://picsum.photos/200/300' },
  { id: 8, name: 'Jane Doe', image: 'https://picsum.photos/200/300' },
  { id: 9, name: 'John Smith', image: 'https://picsum.photos/200/300' },
];

export const TinderSwipe = () => {
  const [cards, setCards] = useState(cardsData);

  const onSwipeLeft = (id: number) => {
    setTimeout(() => {
      setCards((old) => old.filter((card) => card.id !== id));
    }, 300);
  };
  const onSwipeRight = (id: number) => {
    setTimeout(() => {
      setCards((old) => old.filter((card) => card.id !== id));
    }, 300);
  };

  return (
    <View className="h-full w-full flex-1 items-center justify-center">
      {cards.map((card) => (
        <TinderCard
          key={card.id}
          {...card}
          onSwipeLeft={() => onSwipeLeft(card.id)}
          onSwipeRight={() => onSwipeRight(card.id)}
        />
      ))}
    </View>
  );
};