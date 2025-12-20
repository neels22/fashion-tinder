import { Text, View, Button, StyleSheet, Image } from "react-native";
import axios from "axios";
import React, { useState } from "react";
import * as ImagePicker from 'expo-image-picker';

const API_URL = "http://10.0.0.108:8000";


export default function Index() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [image, setImage] = useState<string | null>(null);

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
      mediaTypes: ['images', 'videos'],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    console.log(result);

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      console.log(result.assets[0].uri);
      uploadImage(result.assets[0].uri);
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
  

    

    
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        padding: 20,
      }}
    >
      <Text style={{ fontSize: 18, marginBottom: 20 }}>Hey there! I am indraneel</Text>

      <Button title="Pick Image" color="blue" onPress={pickImage} />

      <Button 
        title={loading ? "Generating..." : "Generate Image"} 
        color="blue" 
        onPress={generateImage}
        disabled={loading}
      />
      
      {data && (
        <View style={{ marginTop: 20, alignItems: "center" }}>
          <Text>Image URL: {data.image_url || 'No URL'}</Text>
          <Text>Image Path: {data.image_path || 'No path'}</Text>
          
          {data.image_url && (
            <Image 
              source={{ uri: `${API_URL}${data.image_url}` }} 
              style={styles.image} 
              resizeMode="contain" 
              onLoad={() => console.log('Image loaded successfully!')}
              onError={(e) => console.log('Image load error:', e.nativeEvent.error)}
            />
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  image: {
    width: 300,
    height: 300,
    borderRadius: 10,
    marginTop: 20,
  },
});