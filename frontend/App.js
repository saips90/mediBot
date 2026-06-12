import { StatusBar } from 'expo-status-bar';
import { Platform } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import ChatScreen from './src/screens/ChatScreen';

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style={Platform.OS === 'web' ? 'light' : 'dark'} />
      <ChatScreen />
    </SafeAreaProvider>
  );
}
