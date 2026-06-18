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

import { loginDemoUser, sendChatMessage } from '../api/chatApi';
import ChatBubble from '../components/ChatBubble';
import MessageInput from '../components/MessageInput';

const demoUsers = [
  { label: 'Doctor', username: 'doctor', password: 'doctor123' },
  { label: 'Nurse', username: 'nurse', password: 'nurse123' },
  { label: 'Billing', username: 'billing', password: 'billing123' },
  { label: 'Technician', username: 'technician', password: 'tech123' },
  { label: 'Admin', username: 'admin', password: 'admin123' },
];

const initialMessages = [
  {
    id: 'welcome',
    role: 'assistant',
    text: 'Hello! I am MediBot. Select a demo role first, then ask a question from that role’s allowed knowledge base.',
  },
];

export default function ChatScreen() {
  const [messages, setMessages] = useState(initialMessages);
  const [isSending, setIsSending] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [session, setSession] = useState(null);
  const listRef = useRef(null);

  async function handleLogin(user) {
    setIsLoggingIn(true);
    try {
      const nextSession = await loginDemoUser(user.username, user.password);
      setSession(nextSession);
      setMessages([
        {
          id: `${Date.now()}-role`,
          role: 'assistant',
          text: `Logged in as ${nextSession.role}. Accessible collections: ${nextSession.collections.join(', ')}.`,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-login-error`,
          role: 'assistant',
          text: error.message,
        },
      ]);
    } finally {
      setIsLoggingIn(false);
    }
  }

  async function handleSend(text) {
    if (!session?.token) {
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-missing-role`,
          role: 'assistant',
          text: 'Please select a demo user role before asking MediBot.',
        },
      ]);
      return;
    }

    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text,
    };

    setMessages((current) => [...current, userMessage]);
    setIsSending(true);

    try {
      const reply = await sendChatMessage(text, session.token);
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: reply.answer,
          retrievalType: reply.retrieval_type,
          sources: reply.sources,
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
            <Text style={styles.statusText}>{session ? session.role : 'Select role'}</Text>
          </View>
        </View>

        <View style={styles.rolePanel}>
          <View style={styles.roleIntro}>
            <Text style={styles.eyebrow}>Role-based access control</Text>
            <Text style={styles.roleTitle}>Choose a MediAssist demo user</Text>
            <Text style={styles.roleText}>
              MediBot filters Qdrant retrieval by role, then shows the allowed collections and sources used for each answer.
            </Text>
          </View>
          <View style={styles.roleGrid}>
            {demoUsers.map((user) => {
              const active = session?.username === user.username;
              return (
                <Pressable
                  key={user.username}
                  disabled={isLoggingIn}
                  onPress={() => handleLogin(user)}
                  style={[styles.roleButton, active && styles.roleButtonActive]}
                >
                  <Text style={[styles.roleButtonTitle, active && styles.roleButtonTitleActive]}>
                    {user.label}
                  </Text>
                  <Text style={[styles.roleButtonMeta, active && styles.roleButtonMetaActive]}>
                    {user.username}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </View>

        {session ? (
          <View style={styles.accessPanel}>
            <View>
              <Text style={styles.accessLabel}>Active role</Text>
              <Text style={styles.accessValue}>{session.role}</Text>
            </View>
            <View style={styles.collectionList}>
              {session.collections.map((collection) => (
                <Text key={collection} style={styles.collectionPill}>
                  {collection}
                </Text>
              ))}
            </View>
          </View>
        ) : null}

        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          style={styles.chatShell}
        >
          <View style={styles.chatHeader}>
            <View>
              <Text style={styles.chatTitle}>MediBot Chat</Text>
              <Text style={styles.chatSubtitle}>
                {session
                  ? `Authenticated as ${session.username}; answers use ${session.role} permissions.`
                  : 'Select a role above to unlock chat.'}
              </Text>
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

          <MessageInput disabled={isSending || !session} onSend={handleSend} />
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
  rolePanel: {
    alignSelf: 'center',
    flexDirection: 'row',
    gap: 24,
    justifyContent: 'space-between',
    maxWidth: 1120,
    paddingBottom: 16,
    paddingTop: 30,
    width: '100%',
  },
  roleIntro: {
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
  roleTitle: {
    color: '#083344',
    fontSize: 30,
    fontWeight: '900',
    lineHeight: 36,
  },
  roleText: {
    color: '#475569',
    fontSize: 15,
    lineHeight: 23,
    marginTop: 10,
  },
  roleGrid: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    justifyContent: 'flex-end',
  },
  roleButton: {
    backgroundColor: '#ffffff',
    borderColor: '#bae6fd',
    borderRadius: 8,
    borderWidth: 1,
    minWidth: 128,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  roleButtonActive: {
    backgroundColor: '#0891b2',
    borderColor: '#0891b2',
  },
  roleButtonTitle: {
    color: '#0f172a',
    fontSize: 15,
    fontWeight: '900',
  },
  roleButtonTitleActive: {
    color: '#ffffff',
  },
  roleButtonMeta: {
    color: '#475569',
    fontSize: 12,
    marginTop: 4,
  },
  roleButtonMetaActive: {
    color: '#cffafe',
  },
  accessPanel: {
    alignItems: 'center',
    alignSelf: 'center',
    backgroundColor: '#ffffff',
    borderColor: '#bae6fd',
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: 'row',
    gap: 16,
    justifyContent: 'space-between',
    marginBottom: 16,
    maxWidth: 1120,
    padding: 14,
    width: '100%',
  },
  accessLabel: {
    color: '#64748b',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  accessValue: {
    color: '#0f172a',
    fontSize: 18,
    fontWeight: '900',
    marginTop: 2,
  },
  collectionList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    justifyContent: 'flex-end',
  },
  collectionPill: {
    backgroundColor: '#ecfeff',
    borderColor: '#bae6fd',
    borderRadius: 999,
    borderWidth: 1,
    color: '#0e7490',
    fontSize: 12,
    fontWeight: '800',
    paddingHorizontal: 10,
    paddingVertical: 6,
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
