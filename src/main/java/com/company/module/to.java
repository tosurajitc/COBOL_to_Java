package com.company.module;

/**
 * Utility class to convert strings to lower or upper case based on a given flag.
 */
public class StringCaseConverter {

    /**
     * Converts the input string to lower or upper case based on the provided flag.
     *
     * @param inputString The string to be converted.
     * @param flag       The flag determining the case conversion. 'l' or 'L' for lowercase,
     *                  'u' or 'U' for uppercase. Any other value results in no conversion.
     * @return The converted string or the original string if the flag is invalid.
     */
    public String convertString(String inputString, String flag) {
        if (inputString == null) {
            return null;
        }
        if (flag == null || flag.isEmpty()) {
            return inputString;
        }
        char caseFlag = flag.charAt(0);
        switch (Character.toUpperCase(caseFlag)) {
            case 'L':
                return inputString.toLowerCase();
            case 'U':
                return inputString.toUpperCase();
            default:
                return inputString;
        }
    }
}