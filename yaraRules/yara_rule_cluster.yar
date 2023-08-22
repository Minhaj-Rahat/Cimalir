/*
    This Yara ruleset is under the GNU-GPLv2 license (http://www.gnu.org/licenses/gpl-2.0.html) and open to any user or organization, as long as you use it under this license.

*/

rule string_match {

    meta:
        author = "anonymous_X"
        description = "String Match to Compare Operaional Similarity"
        version = "1.0"
    strings:
        $s1 = "NICK"
        $s2 = "PING"
        $s3 = "JOIN"
        $s4 = "USER"
        $s5 = "PRIVMSG"
        
        
	$s8 = "/proc/net/route"
	$s9 = "admin"
	$s10 = "root"
	$s11 = "sockprintf"
	
	$s12 = "3AES"
        $s13 = "Hacker"
        $s14 = "VERSONEX"
        
    condition:
        1 of them
}
