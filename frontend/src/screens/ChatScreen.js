import { useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { sendChatMessage } from '../api/chatApi';
import ChatBubble from '../components/ChatBubble';
import MessageInput from '../components/MessageInput';

const initialMessages = [
  {
    id: 'welcome',
    role: 'assistant',
    text: 'Hello! I am Medibudi. Ask me a medical question and I will answer from the backend knowledge base.',
  },
];

export default function ChatScreen() {
  const [messages, setMessages] = useState(initialMessages);
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef(null);

  async function handleSend(text) {
    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text,
    };

    setMessages((current) => [...current, userMessage]);
    setIsSending(true);

    try {
      const reply = await sendChatMessage(text);
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: reply,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-error`,
          role: 'assistant',
          text: error.message,
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.container}
      >
        <View style={styles.header}>
          <View style={styles.logo}>
            <Text style={styles.logoText}>M</Text>
          </View>
          <View>
            <Text style={styles.title}>Medibudi</Text>
            <Text style={styles.subtitle}>Medical RAG Assistant</Text>
          </View>
        </View>

        <FlatList
          ref={listRef}
          contentContainerStyle={styles.messages}
          data={messages}
          keyExtractor={(item) => item.id}
          onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
          renderItem={({ item }) => <ChatBubble message={item} />}
        />

        {isSending ? (
          <View style={styles.loadingRow}>
            <ActivityIndicator color="#0ea5e9" />
            <Text style={styles.loadingText}>Medibudi is thinking...</Text>
          </View>
        ) : null}

        <MessageInput disabled={isSending} onSend={handleSend} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  container: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderBottomColor: '#e2e8f0',
    borderBottomWidth: 1,
    flexDirection: 'row',
    gap: 12,
    paddingHorizontal: 18,
    paddingVertical: 14,
  },
  logo: {
    alignItems: 'center',
    backgroundColor: '#0ea5e9',
    borderRadius: 14,
    height: 44,
    justifyContent: 'center',
    width: 44,
  },
  logoText: {
    color: '#ffffff',
    fontSize: 22,
    fontWeight: '800',
  },
  title: {
    color: '#0f172a',
    fontSize: 20,
    fontWeight: '800',
  },
  subtitle: {
    color: '#64748b',
    fontSize: 13,
    marginTop: 2,
  },
  messages: {
    padding: 16,
  },
  loadingRow: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 16,
    paddingBottom: 8,
  },
  loadingText: {
    color: '#64748b',
    fontSize: 13,
  },
});
