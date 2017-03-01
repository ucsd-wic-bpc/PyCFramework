/*
 * jsonFASTParse
 * @author: Brandon Milton
 * http://brandonio21.com
 *
 * A small Java library meant to parse JSON in a quick fashion, given that the
 * end-user is aware of the JSON data schema. Does not support dictionaries.
 */

class JSONList extends JSONObject {
  public ArrayList<JSONObject> entries;
  private  Dictionary<Character, Character> wrapCharacters;

  public JSONList(String data) {
    this.entries = new ArrayList<JSONObject>();
    this.wrapCharacters = new Hashtable<Character, Character>();
    wrapCharacters.put('[', ']');
    wrapCharacters.put('"', '"');
    this.populateEntriesFromString(data);
  }

  public int getEntryCount() {
    return this.entries.size();
  }

  public JSONObject getItem(int index) {
    return this.entries.get(index);
  }

  private void populateEntriesFromString(String str) {
    Stack<Character> delimiterStack = new Stack<Character>();
    StringBuilder currentString = new StringBuilder();

    for (int i = 0; i < str.length(); i++) {
      if (!delimiterStack.empty() && str.charAt(i) == getClosingDelimFromStack(delimiterStack))
        delimiterStack.pop();
      else if (isDelimiterCharacter(str.charAt(i)))
        delimiterStack.push(str.charAt(i));

      // Check to see if we have reached a comma
      if ((str.charAt(i) == ',' || i == str.length() - 1) && delimiterStack.empty()) {
        // Check if last item
        if (i == str.length() - 1) currentString.append(str.charAt(i));
        this.entries.add(JSONParser.getObjectFromString(currentString.toString()));
        currentString.delete(0, currentString.length());
        continue;
      }
      currentString.append(str.charAt(i));
    }
  }

  private boolean isDelimiterCharacter(char c) {
    return this.wrapCharacters.get(c) != null;
  }

  private char getClosingDelimFromStack(Stack<Character> stack) {
    return this.wrapCharacters.get(stack.peek());
  }
}

class JSONObject {
  private String data;

  public JSONObject() {
    this.data = "";
  }

  public JSONObject(String data) {
    this.data = data;
  }

  public String getData() {
    return this.data;
  }

  public int castToInt() {
    return Integer.parseInt(this.data);
  }

  public double castToDouble() {
    return Double.parseDouble(this.data);
  }

  public char castToChar() {
    return this.data.charAt(0);
  }
}

class JSONParser {

  public static JSONObject getObjectFromString(String str) {
    // Check if surrounded by quotes, list brackets, or nothing
    if (str.charAt(0) == '[' && str.charAt(str.length() - 1) == ']')
      return new JSONList(str.substring(1, str.length() - 1));
    else if (str.charAt(0) == '"' && str.charAt(str.length() - 1) == '"')
      return new JSONObject(str.substring(1, str.length() - 1));
    else
      return new JSONObject(str);
  }

}
