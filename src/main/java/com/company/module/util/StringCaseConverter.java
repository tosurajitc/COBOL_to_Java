package com.company.module.util;

/**
 * Utility class for converting strings to lower or upper case based on a flag.
 */
public class StringCaseConverter {

    /**
     * Converts the given string to lower or upper case based on the specified flag.
     *
     * @param inputStr the input string to be converted
     * @param flag     a single character 'l', 'L', 'u', or 'U' to determine the case conversion
     * @return the converted string in lower or upper case, or the original string if the flag is invalid
     */
    public static String convertStringCase(String inputStr, String flag) {
        if (inputStr == null || flag == null) {
            return inputStr;
        }

        char flagChar = flag.charAt(0);
        if (flagChar == 'l' || flagChar == 'L') {
            return inputStr.toLowerCase();
        } else if (flagChar == 'u' || flagChar == 'U') {
            return inputStr.toUpperCase();
        } else {
            return inputStr;
        }
    }
}