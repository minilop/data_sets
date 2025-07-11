package sql

import (
	"fmt"
	"regexp"
	"strings"
	"unicode/utf8"
)

const (
	sql_sign       = "[,;.\\\\]{1}"                                                                                                                                                                          //匹配符号
	sql_blank      = "[\\s\\n\\t'\"`]{1}"                                                                                                                                                                    //匹配空格等不可见字符和单引号双引号
	sql_calc       = "[\\+\\-\\*/]{1}"                                                                                                                                                                       // 匹配运算符
	sql_inequality = "!=?|>=?|<=?|[>=<]{1}"                                                                                                                                                                  //匹配不等式
	sql_sub        = "[\\(\\)]{1}"                                                                                                                                                                           //匹配圆括号
	sql_num        = "[1-9.e]+"                                                                                                                                                                              //匹配数字
	sql_char       = "[^,;.\\\\'\"`\\+\\-\\*/!=><\\(\\)\\s\\n\\t]+"                                                                                                                                          //匹配字符
	sql_keys       = "(?i)\\b(SELECT\\s+DISTINCT|SELECT|FROM|WHERE|GROUP\\s+BY|HAVING|ORDER\\s+BY|LEFT\\s+OUTER\\s+JOIN|RIGHT\\s+OUTER\\s+JOIN|LEFT\\s+JOIN|RIGHT\\s+JOIN|JOIN|UNION\\s+ALL|UNION|LIMIT)\\b" // 匹配组合关键字
	sql_cut        = sql_sign + "|" + sql_blank + "|" + sql_num + "|" + sql_calc + "|" + sql_inequality + "|" + sql_sub + "|" + sql_keys + "|" + sql_char
)

var quote = map[string]bool{
	SINGLE_QUOTE: true,
	DOUBLE_QUOTE: true,
	BACK_QUOTE:   true,
}

func Tokenize(sql string) tokenSeq {
	re := regexp.MustCompile(sql_cut)
	found := re.FindAllString(sql, -1)
	tokens := []string{}
	if found == nil {
		fmt.Println("no match")
	}
	tokens = append(tokens, found...)
	return tokenSeq{sql: sql, tokens: tokens}
}

type strContext struct {
	chars  []string
	lineno int
	colno  int
}

func (sc *strContext) check() bool {
	flag := false
	if sc.chars[len(sc.chars)-2] != "\\" && sc.chars[len(sc.chars)-1] == sc.chars[0] {
		flag = true
	}
	return flag
}

func (sc *strContext) str() string {
	return strings.Join(sc.chars, "")
}

type tokenSeq struct {
	sql    string
	tokens []string
}

type Token struct {
	Lineno int
	Colno  int
	Value  string
	prev   *Token
}

func (t *Token) Lower() string {
	return strings.TrimSpace(strings.ToLower(t.Value))
}

func (t *Token) IsStr() bool {
	return IsStr(t.Value)
}

func (t *Token) IsNum() bool {
	return IsNum(t.Value)
}

func (t *tokenSeq) Parse() []*Token {
	var str_ctx strContext
	var lineno = 1
	var colno = 1

	var tokens = []*Token{}

	var prev *Token = nil

	for _, token := range t.tokens {
		if token == NEW_LINE {
			lineno += 1
			colno = 0
		}

		if RemoveBlank(token) != NO_NEAR {
			if quote[token] && str_ctx.chars == nil {
				str_ctx = strContext{[]string{token}, lineno, colno}
			} else if str_ctx.chars != nil {
				str_ctx.chars = append(str_ctx.chars, token)
				if str_ctx.check() {
					t := Token{lineno, colno, str_ctx.str(), prev}
					tokens = append(tokens, &t)
					prev = &t
					str_ctx.chars = nil
					str_ctx.lineno = 0
					str_ctx.colno = 0
				}
			} else {
				t := Token{lineno, colno, token, prev}
				tokens = append(tokens, &t)
				prev = &t
			}
		}

		colno += utf8.RuneCountInString(token)
	}

	if str_ctx.chars != nil {
		panic(fmt.Sprintf("字符串没有闭合: line: %d, column: %d", str_ctx.lineno, str_ctx.colno))
	}

	return tokens
}
