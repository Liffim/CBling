
#######################################
# IMPORTS
#######################################

from strings_with_arrows import *
#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name #error name
        self.details = details #details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n' # returns error name and details as string
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end) # string with arrows show arrows to where the error is
        return result

class IllegalCharError(Error):
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error): #if error in syntax
		def __init__(self, pos_start, pos_end, details=''):
				super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx # index
        self.ln = ln #line number
        self.col = col #collum number
        self.fn = fn #file name
        self.ftxt = ftxt # file text

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n': #if new line reset the colum
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)
#######################################
# TOKENS
#######################################

TT_INT		= 'INT' #Types
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF		= 'EOF' #END OF FILE

class Token:
		def __init__(self, type_, value=None, pos_start=None, pos_end=None): # Type and value, value can be non existant
				self.type = type_
				self.value = value

				if pos_start: #to show where the error is
					self.pos_start = pos_start.copy()
					self.pos_end = pos_start.copy()
					self.pos_end.advance()

				if pos_end: #to show where the error is
					self.pos_end = pos_end
		
		def __repr__(self):
				if self.value: return f'{self.type}:{self.value}'# print type and value if no value print type
				return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text #text we are processing
        self.pos = Position(-1, 0, -1, fn, text) # position, pos -1 because goes to Position and does +1
        self.current_char = None # current char
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None #sets to the character if pos is inside the text

    def make_tokens(self): #making tokens
        tokens = [] # empty list of tokens

        while self.current_char != None: # goes to each character through the text
            if self.current_char in ' \t': #ingores tarpai ir \t
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy() # for error 
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'") #returns error character
        tokens.append(Token(TT_EOF, pos_start=self.pos)) #END OF FILE
        return tokens, None

    def make_number(self):
        num_str = '' # number in string form
        dot_count = 0 # if float chech position of dot
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':# 
                if dot_count == 1: break # breaks if there is 2 dots
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char # makes a new number
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str)) # returns int if dot_count is 0
        else:
            return Token(TT_FLOAT, float(num_str))# else retusn float

#######################################
# NODES
#######################################
#imagine veiksmai veikia pagal medi

class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}' #returns token in a string

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node): #add, subtract, divide, multiply operation priority
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})' #returns string

class UnaryOpNode: #to check where is a - infront of a number
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT # to check if there was any errors
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None

	def register(self, res):
		if isinstance(res, ParseResult):# if result is parse result
			if res.error: self.error = res.error # if the result has an error we set the error
			return res.node

		return res

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		self.error = error # takes in the error
		return self

#######################################
# PARSER
#######################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1 #current token index
		self.advance() #index method

	def advance(self, ):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens): #if in range of tokens -> grab the token
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.expr()
		if not res.error and self.current_tok.type != TT_EOF: # shows that there is code to proccess != TT_EOF
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '+', '-', '*' or '/'"
			))
		return res

	###################################

	def factor(self):
		res = ParseResult() # parse result instance
		tok = self.current_tok #current token

		if tok.type in (TT_PLUS, TT_MINUS): #to check if there is a minus or plus infront of a number
			res.register(self.advance()) 
			factor = res.register(self.factor())
			if res.error: return res
			return res.success(UnaryOpNode(tok, factor)) #creates unarynode
		
		elif tok.type in (TT_INT, TT_FLOAT): #check if the token is int or float
			res.register(self.advance()) # ep 4 paaiškina kodėl reikalingas
			return res.success(NumberNode(tok)) #returns number node of that token# passes final result

		elif tok.type == TT_LPAREN:# (
			res.register(self.advance())
			expr = res.register(self.expr())
			if res.error: return res
			if self.current_tok.type == TT_RPAREN: #looks for )
				res.register(self.advance())
				return res.success(expr)
			else:#if syntax failes (there is no ) to end the parenthesis) 
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	###################################

	def bin_op(self, func, ops): #operation tokens, functions from grammer.txt
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops: #while the token is the current given one
			op_tok = self.current_tok # grab that token
			res.register(self.advance())
			right = res.register(func()) # grab the factor
			if res.error: return res
			left = BinOpNode(left, op_tok, right) # binary oporation between them

		return res.success(left)
#######################################
# RUN
#######################################

def run(fn, text):
		# Generate tokens
		lexer = Lexer(fn, text) # pass the lexer our text
		tokens, error = lexer.make_tokens()
		if error: return None, error
		
		# Generate AST
		parser = Parser(tokens)
		ast = parser.parse()

		return ast.node, ast.error