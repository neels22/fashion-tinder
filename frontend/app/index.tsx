import { Text, View, Button, StyleSheet, Image, ScrollView } from "react-native";
import axios from "axios";
import React, { useState } from "react";
import * as ImagePicker from 'expo-image-picker';
import { verifyInstallation } from 'nativewind';
import { TinderCard } from '../components/tinder-card';
const API_URL = "http://10.0.0.108:8000";


export default function Index() {
  verifyInstallation();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState<string | null>(null);
  const [multipleImages, setMultipleImages] = useState<any>(null);
  const [visibleImages, setVisibleImages] = useState<any>(null);

  const generateImage = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/single_image`);
      console.log('API Response:', JSON.stringify(response.data, null, 2));
      console.log('Image URL:', response.data.image_url);
      console.log('Image Path:', response.data.image_path);
      setData(response.data);
    } catch (error) {
      console.error('Error generating image:', error);
    } finally {
      setLoading(false);
    }
  };

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permissionResult.granted) {
      alert('permissions not granted');
      return;
    }
    
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 1,
    });

    console.log(result);

    if (!result.canceled) {
      const selectedImage = result.assets[0];
      console.log('Selected image URI:', selectedImage.uri);
      console.log('Dimensions:', `${selectedImage.width}x${selectedImage.height}`);
      
      setImage(selectedImage.uri);
      uploadImage(selectedImage.uri);
    }
  };

  const uploadImage = async (imageUri: string) => {
    try {
      const formData = new FormData();
      
      // Extract filename from URI
      const filename = imageUri.split('/').pop() || 'photo.jpg';
      
      // Determine file type
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image/jpg`;
      
      // Append file with proper structure for React Native
      formData.append('file', {
        uri: imageUri,
        name: filename,
        type: type,
      } as any);
      
      const response = await axios.post(`${API_URL}/upload_image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(response.data);
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  const generateMultipleImages = async() =>{
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/multiple_images`);
      console.log('API Response:', JSON.stringify(response.data, null, 2));
      setMultipleImages(response.data);
      setVisibleImages(response.data);
      console.log('Multiple Images:', multipleImages);
    }
    catch(error){
      console.error('Error generating multiple images:', error);
    }
    finally{
      setLoading(false);
    }
  }

  const removeTopCard = () => {
    setTimeout(() => {
      setVisibleImages((prev: any) => {
        if (!prev || prev.length === 0) return prev;
        // Remove the last card (last rendered = top of stack)
        return prev.slice(0, -1);
      });
    }, 400); // Wait for swipe animation to complete
  };
    

    
  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View className="bg-blue-500 p-4 rounded-lg mb-4">
        <Text className="text-xl font-semibold text-white">Hey there! I am indraneel</Text>
        <Text className="text-sm text-yellow-300 mt-2">Testing NativeWind styles</Text>
      </View>

      <Button title="Pick Image" color="blue" onPress={pickImage} />

      <Button 
        title={loading ? "Generating..." : "Generate Image"} 
        color="blue" 
        onPress={generateImage}
        disabled={loading}
      />

      <Button
      title={loading ? "Generating Multiple Images..." : "Generate Multiple Images"}
      color="blue"
      onPress={generateMultipleImages}
      disabled={loading}
      />
      
      {data && (
        <View style={{ marginTop: 20, alignItems: "center" }} >
          <Text>Image URL: {data.image_url || 'No URL'}</Text>
          <Text>Image Path: {data.image_path || 'No path'}</Text>
          
          {data.image_url && (
                  <View style={{ height: 500, width: 350, position: 'relative' }}>
                  <TinderCard 
                    image={`${API_URL}${data.image_url}` as string} 
                    onSwipeLeft={() => {
                      console.log('swiped left');
                    }}
                    onSwipeRight={() => {
                      console.log('swiped right');
                    }}
                  />
                </View>
          )}
        </View>
      )}

      {/* {multipleImages &&
          (
            <View style={{ marginTop: 20, alignItems: "center" }}>
              <Text>Multiple Images</Text>

              {multipleImages.map((image: any) => (
                <Image 
                source={{ uri: `${API_URL}${image.image_url}` }} 
                style={styles.image}
                 resizeMode="contain" key={image.image_path}>
                </Image>
              ))}
            </View>
          )} */}

     {visibleImages && visibleImages.length > 0 &&
          (
            <View style={{ marginTop: 20, alignItems: "center" }}>
              <Text>Multiple Images ({visibleImages.length} remaining)</Text>

              <View style={{ height: 500, width: 350, position: 'relative' }}>
              {visibleImages.map((image: any) => (
                <TinderCard 
                image={`${API_URL}${image.image_url}` as string} 
                onSwipeLeft={() => {
                  console.log('swiped left');
                  removeTopCard();
                }}
                onSwipeRight={() => {
                  console.log('swiped right');
                  removeTopCard();
                }}
                key={image.image_path}
                />
              ))}
              </View>
            </View>
          )}
        

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  image: {
    width: 300,
    height: 300,
    borderRadius: 10,
    marginTop: 20,
  },
});


/*
- single image generation is working fine 
- the image is getting displayed in the frontend
- multiple image generation hasnt been tested 
- image upload is working fine 
- will probably show all the images one below another for now 
- the images are present in data object 
- probably will loop through the data object and display the images one below another 
- or better way is to use map i guess 




*/