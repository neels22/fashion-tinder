import { Text, View, Button, StyleSheet, Image } from "react-native";
import axios from "axios";
import React, { useState } from "react";

const API_URL = "http://10.0.0.108:8000";


export default function Index() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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