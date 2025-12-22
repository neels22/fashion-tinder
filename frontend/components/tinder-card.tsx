import { Dimensions, Image } from 'react-native';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from 'react-native-reanimated';
import { scheduleOnRN } from 'react-native-worklets';

const { width } = Dimensions.get('screen');

const SWIPE_THRESHOLD = width * 0.5;

type TinderCardProps = {
  image: string;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
};

export const TinderCard = ({ image, onSwipeLeft, onSwipeRight }: TinderCardProps) => {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);
  const prevTranslationX = useSharedValue(0);
  const prevTranslationY = useSharedValue(0);
  const rotate = useSharedValue(0);

  const PanGesture = Gesture.Pan()
    .onStart((event) => {
      prevTranslationX.value = event.translationX;
      prevTranslationY.value = event.translationY;
    })
    .onUpdate((event) => {
      translateX.value = prevTranslationX.value + event.translationX;
      translateY.value = prevTranslationY.value + Math.min(0, event.translationY);
      rotate.value = event.translationX / 10;
    })
    .onEnd(() => {
      if (translateX.value > SWIPE_THRESHOLD) {
        translateX.value = withTiming(width * 2, { duration: 400 });
        scheduleOnRN(onSwipeRight);
      } else if (translateX.value < -SWIPE_THRESHOLD) {
        translateX.value = withTiming(-width * 2, { duration: 400 });
        scheduleOnRN(onSwipeLeft);
      } else {
        translateX.value = withSpring(0);
        translateY.value = withSpring(0);
        rotate.value = withSpring(0);
      }
    });

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [
        { translateX: translateX.value },
        { translateY: translateY.value },
        { rotate: `${rotate.value}deg` },
      ],
    };
  });

  return (
    <GestureDetector gesture={PanGesture}>
<Animated.View
  style={[
    {
      position: 'absolute',
      height: '100%',
      width: '100%',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 16,
      overflow: 'hidden',
      backgroundColor: '#000', // or any color you prefer
    },
    animatedStyle
  ]}>
  <Image 
    source={{ uri: image }} 
    style={{ height: '100%', width: '100%' }}
    resizeMode="contain"
  />
</Animated.View>
    </GestureDetector>
  );
};