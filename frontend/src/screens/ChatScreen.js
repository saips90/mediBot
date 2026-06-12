import { useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
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
    text: 'Hello! I am MediBot. Ask me a medical question and I will answer from the backend knowledge base.',
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
      <View style={styles.page}>
        <View style={styles.siteHeader}>
          <View style={styles.brand}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>M</Text>
            </View>
            <View>
              <Text style={styles.title}>MediBot</Text>
              <Text style={styles.subtitle}>Medical RAG Assistant</Text>
            </View>
          </View>
          <View style={styles.headerActions}>
            <Text style={styles.statusDot}>●</Text>
            <Text style={styles.statusText}>Backend ready</Text>
          </View>
        </View>

        <View style={styles.hero}>
          <View style={styles.heroCopy}>
            <Text style={styles.eyebrow}>Clinical knowledge support</Text>
            <Text style={styles.heroTitle}>Ask medical questions from your browser.</Text>
            <Text style={styles.heroText}>
              MediBot connects to your backend knowledge base and keeps the chat experience optimized for desktop and tablet web users.
            </Text>
          </View>
          <View style={styles.heroStats}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>RAG</Text>
              <Text style={styles.statLabel}>Grounded answers</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>Web</Text>
              <Text style={styles.statLabel}>Responsive layout</Text>
            </View>
          </View>
        </View>

        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.chatShell}
        >
          <View style={styles.chatHeader}>
            <View>
              <Text style={styles.chatTitle}>MediBot Chat</Text>
              <Text style={styles.chatSubtitle}>Responses are generated from the configured API.</Text>
            </View>
            <Pressable style={styles.secondaryButton} onPress={() => setMessages(initialMessages)}>
              <Text style={styles.secondaryButtonText}>New chat</Text>
            </Pressable>
          </View>

          <FlatList
            ref={listRef}
            contentContainerStyle={styles.messages}
            data={messages}
            keyExtractor={(item) => item.id}
            onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: true })}
            renderItem={({ item }) => <ChatBubble message={item} />}
            style={styles.messageList}
          />

          {isSending ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator color="#0891b2" />
              <Text style={styles.loadingText}>MediBot is thinking...</Text>
            </View>
          ) : null}

          <MessageInput disabled={isSending} onSend={handleSend} />
        </KeyboardAvoidingView>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ecfeff',
  },
  page: {
    flex: 1,
    backgroundColor: '#ecfeff',
    paddingHorizontal: 24,
    paddingVertical: 20,
  },
  siteHeader: {
    alignItems: 'center',
    alignSelf: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
    maxWidth: 1120,
    width: '100%',
  },
  brand: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: 12,
  },
  logo: {
    alignItems: 'center',
    backgroundColor: '#0891b2',
    borderRadius: 12,
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
    color: '#164e63',
    fontSize: 20,
    fontWeight: '800',
  },
  subtitle: {
    color: '#475569',
    fontSize: 13,
    marginTop: 2,
  },
  headerActions: {
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderColor: '#bae6fd',
    borderRadius: 999,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  statusDot: {
    color: '#10b981',
    fontSize: 12,
  },
  statusText: {
    color: '#0f172a',
    fontSize: 13,
    fontWeight: '700',
  },
  hero: {
    alignSelf: 'center',
    flexDirection: 'row',
    gap: 24,
    justifyContent: 'space-between',
    maxWidth: 1120,
    paddingBottom: 24,
    paddingTop: 52,
    width: '100%',
  },
  heroCopy: {
    flex: 1,
    maxWidth: 650,
  },
  eyebrow: {
    color: '#0891b2',
    fontSize: 13,
    fontWeight: '800',
    letterSpacing: 0,
    marginBottom: 10,
    textTransform: 'uppercase',
  },
  heroTitle: {
    color: '#083344',
    fontSize: 44,
    fontWeight: '900',
    lineHeight: 50,
  },
  heroText: {
    color: '#475569',
    fontSize: 17,
    lineHeight: 26,
    marginTop: 14,
  },
  heroStats: {
    alignSelf: 'flex-end',
    flexDirection: 'row',
    gap: 12,
  },
  stat: {
    backgroundColor: '#ffffff',
    borderColor: '#bae6fd',
    borderRadius: 8,
    borderWidth: 1,
    minWidth: 132,
    padding: 16,
  },
  statValue: {
    color: '#0e7490',
    fontSize: 24,
    fontWeight: '900',
  },
  statLabel: {
    color: '#475569',
    fontSize: 13,
    marginTop: 4,
  },
  chatShell: {
    alignSelf: 'center',
    backgroundColor: '#ffffff',
    borderColor: '#bae6fd',
    borderRadius: 8,
    borderWidth: 1,
    flex: 1,
    maxHeight: 720,
    maxWidth: 1120,
    overflow: 'hidden',
    width: '100%',
  },
  chatHeader: {
    alignItems: 'center',
    borderBottomColor: '#e2e8f0',
    borderBottomWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  chatTitle: {
    color: '#0f172a',
    fontSize: 18,
    fontWeight: '800',
  },
  chatSubtitle: {
    color: '#64748b',
    fontSize: 13,
    marginTop: 3,
  },
  secondaryButton: {
    backgroundColor: '#f0fdfa',
    borderColor: '#99f6e4',
    borderRadius: 8,
    borderWidth: 1,
    paddingHorizontal: 14,
    paddingVertical: 9,
  },
  secondaryButtonText: {
    color: '#0f766e',
    fontSize: 13,
    fontWeight: '800',
  },
  messageList: {
    flex: 1,
  },
  messages: {
    padding: 20,
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
