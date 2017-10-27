#ifndef HASH_H
#define HASH_H

#include "reversi.h"

struct slot{
	board brd;
	calc_type alpha, beta;
	short depth;
	pos_type pos;
};

class tank{
protected:
	static const int size = 15084637;
	slot* table;

public:
	tank(){
		table = new slot[size];
	}
	tank(const tank& tnk){
		table = new slot[size];
		memcpy(table, tnk.table,sizeof(slot) * size);
	}
	tank(tank&& tnk){
		table = tnk.table;
		tnk.table = NULL;
	}
	~tank(){
		delete table;
	}
	tank& operator=(const tank& tnk){
		memcpy(table, tnk.table,sizeof(slot) * size);
		return *this;
	}
	tank& operator=(tank&& tnk){
		delete table;
		table = tnk.table;
		tnk.table = NULL;
		return *this;
	}
	size_t mapping(cbool color,cboard brd){
		return (
			brd.bget(true) * 3727042349078977
			+ brd.bget(false) * 9109418502615479
			+ color
		) % size;
	}
	void clear(){
		for(int i = 0;i != size;++i){
			slot& slt = table[i];
			slt.brd.assign(0,0);
			slt.depth = 0;
			slt.alpha = _inf;
			slt.beta = inf;
		}
	}
	void insert(cbool color,const slot& slt){
		table[mapping(color,slt.brd)] = slt;
	}
	slot& find(cbool color,cboard brd){
		return table[mapping(color,brd)];
	}
};

#endif //HASH_H
