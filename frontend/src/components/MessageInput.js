import { Ionicons } from '@expo/vector-icons';
import { useState } from 'react';
import { Pressable, StyleSheet, TextInput, View } from 'react-native';

export default function MessageInput({ disabled, onSend }) {
  const [value, setValue] = useState('');

  function handleSend() {
    const text = value.trim();
    if (!text || disabled) return;

    setValue('');
    onSend(text);
  }

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={setValue}
        placeholder="Ask Medibudi..."
        placeholderTextColor="#64748b"
        editable={!disabled}
        multiline
      />
      <Pressable
        accessibilityLabel="Send message"
        disabled={disabled || !value.trim()}
        onPress={handleSend}
        style={({ pressed }) => [
          styles.button,
          (disabled || !value.trim()) && styles.buttonDisabled,
          pressed && styles.buttonPressed,
        ]}
      >
        <Ionicons name="send" color="#ffffff" size={18} />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
    borderTopColor: '#e2e8f0',
    borderTopWidth: 1,
    padding: 12,
    backgroundColor: '#ffffff',
  },
  input: {
    flex: 1,
    maxHeight: 120,
    minHeight: 46,
    borderColor: '#cbd5e1',
    borderRadius: 18,
    borderWidth: 1,
    color: '#0f172a',
    fontSize: 16,
    paddingHorizontal: 14,
    paddingVertical: 11,
  },
  button: {
    alignItems: 'center',
    backgroundColor: '#0ea5e9',
    borderRadius: 18,
    height: 46,
    justifyContent: 'center',
    width: 46,
  },
  buttonDisabled: {
    backgroundColor: '#94a3b8',
  },
  buttonPressed: {
    opacity: 0.85,
  },
});
